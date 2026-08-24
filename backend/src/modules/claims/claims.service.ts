import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
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

    const claim = await this.prisma.claim.create({
      data: {
        title: dto.title,
        description: dto.description,
        externalId,
        status: ClaimStatus.SUBMITTED,
        creatorId: userId,
        companyId,
      },
    });

    try {
      const glResult = await this.genlayer.createClaim({
        externalId,
        title: dto.title,
        description: dto.description,
        evidenceUrls: dto.evidenceUrls || '',
        plaintiff: dto.plaintiff || '',
        defendant: dto.defendant || 'unknown',
        templateId: dto.templateId || 'general',
        jurisdiction: dto.jurisdiction || '',
      });

      await this.prisma.claim.update({
        where: { id: claim.id },
        data: {
          genlayerClaimId: glResult.claimId,
          status: ClaimStatus.AI_REVIEWING,
        },
      });

      return { ...claim, genlayerClaimId: glResult.claimId };
    } catch (error) {
      return claim;
    }
  }

  async findAll(companyId?: string) {
    return this.prisma.claim.findMany({
      where: companyId ? { companyId } : undefined,
      include: {
        evidence: true,
        aiResolution: true,
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
        aiResolution: true,
        humanReviews: {
          include: { reviewer: { select: { id: true, name: true } } },
        },
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

    const result = await this.genlayer.resolveClaim(claim.genlayerClaimId);
    const r = result.resolution || {};

    await this.prisma.aiResolution.upsert({
      where: { claimId: id },
      create: {
        claimId: id,
        decision: r.decision || 'INVALID',
        confidence: r.confidence || 0,
        reasoning: r.reasoning || null,
        isReassessment: !!r.is_reassessment,
        rawResponse: r,
      },
      update: {
        decision: r.decision || 'INVALID',
        confidence: r.confidence || 0,
        reasoning: r.reasoning || null,
        isReassessment: !!r.is_reassessment,
        rawResponse: r,
      },
    });

    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.AI_RESOLVED },
    });

    return result;
  }

  async challenge(id: string, reason: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) throw new BadRequestException('No GenLayer claim');

    await this.genlayer.challengeClaim(claim.genlayerClaimId, reason);
    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.CHALLENGED },
    });
    return { success: true };
  }

  async appeal(id: string, reason: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) throw new BadRequestException('No GenLayer claim');

    await this.genlayer.appealClaim(claim.genlayerClaimId, reason);
    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.CHALLENGED }, // یا وضعیت APPEALED اگر به enum اضافه کردی
    });
    return { success: true };
  }

  async finalize(id: string) {
    const claim = await this.findOne(id);
    if (!claim.genlayerClaimId) throw new BadRequestException('No GenLayer claim');

    await this.genlayer.finalizeClaim(claim.genlayerClaimId);
    await this.prisma.claim.update({
      where: { id },
      data: { status: ClaimStatus.FINALIZED },
    });
    return { success: true };
  }
}