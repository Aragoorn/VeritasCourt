import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { GenlayerService } from '../genlayer/genlayer.service';
import { CreateClaimDto } from './dto/create-claim.dto';
import { ClaimStatus } from '@prisma/client';

@Injectable()
export class ClaimsService {
  constructor(
    private prisma: PrismaService,
    private genlayer: GenlayerService,
  ) {}

  async create(dto: CreateClaimDto, userId: string, companyId: string) {
    const externalId = dto.externalId || `claim-${Date.now()}`;

    // اول در قرارداد بساز
    const glResult = await this.genlayer.createClaim({
      externalId,
      title: dto.title,
      description: dto.description,
      evidenceUrls: dto.evidenceUrls || '',
      plaintiff: dto.plaintiff || '',
      defendant: dto.defendant || '0x0000000000000000000000000000000000000001',
      templateId: dto.templateId || 'general',
      jurisdiction: dto.jurisdiction || '',
    });

    // سپس فقط برای ایندکس در دیتابیس ذخیره کن
    const claim = await this.prisma.claim.create({
      data: {
        title: dto.title,
        description: dto.description,
        externalId,
        status: ClaimStatus.SUBMITTED,
        creatorId: userId,
        companyId,
        genlayerClaimId: String(glResult.claimId),
      },
    });

    return claim;
  }

  async findAll(companyId?: string) {
    return this.prisma.claim.findMany({
      where: companyId ? { companyId } : undefined,
      include: {
        evidence: true,
        creator: { select: { id: true, name: true, email: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string) {
    const claim = await this.prisma.claim.findUnique({
      where: { id },
      include: {
        evidence: true,
        creator: { select: { id: true, name: true, email: true } },
      },
    });
    if (!claim) throw new NotFoundException('Claim not found');
    return claim;
  }

  async resolve(id: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) {
      throw new BadRequestException('Claim not submitted to GenLayer');
    }

    // فقط قرارداد را صدا بزن
    const result = await this.genlayer.resolveClaim(claim.genlayerClaimId);

    // فقط وضعیت را آپدیت کن (منبع حقیقت قرارداد است)
    await this.prisma.claim.update({
      where: { id },
      data: {
        status: ClaimStatus.RESOLVED,
        lastDecision: result?.decision || null,
        lastConfidence: result?.confidence || null,
      },
    });

    return result;
  }

  async challenge(id: string, reason: string, value?: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) {
      throw new BadRequestException('No GenLayer claim');
    }

    // value باید ارسال شود (قرارداد zero را رد می‌کند)
    await this.genlayer.challengeClaim(
      claim.genlayerClaimId,
      reason,
      value, // مهم
    );

    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.CHALLENGED },
    });

    return { success: true };
  }

  async appeal(id: string, reason: string, value?: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) {
      throw new BadRequestException('No GenLayer claim');
    }

    await this.genlayer.appealClaim(
      claim.genlayerClaimId,
      reason,
      value,
    );

    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.APPEALED },
    });

    return { success: true };
  }

  /**
   * مسیر صحیح human review – فقط از طریق قرارداد
   */
  async castHumanVote(id: string, vote: 'VALID' | 'PARTIALLY_VALID' | 'INVALID') {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) {
      throw new BadRequestException('No GenLayer claim');
    }

    const result = await this.genlayer.castHumanVote(
      claim.genlayerClaimId,
      vote,
    );

    return result;
  }

  /**
   * Finalization فقط و فقط on-chain
   * هیچ finalization در Prisma انجام نمی‌شود
   */
  async finalizeOnChain(id: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) {
      throw new BadRequestException('No GenLayer claim');
    }

    // فقط قرارداد را صدا بزن
    const result = await this.genlayer.finalizeClaim(claim.genlayerClaimId);

    // فقط فلگ را برای نمایش آپدیت کن
    await this.prisma.claim.update({
      where: { id },
      data: {
        status: ClaimStatus.FINALIZED,
        finalizedOnChain: true,
      },
    });

    return {
      success: true,
      on_chain: true,
      prisma_path_used: false,
      result,
    };
  }
}
