import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { ClaimStatus } from '@prisma/client';

@Injectable()
export class ReviewService {
  constructor(private prisma: PrismaService) {}

  async requestHumanReview(claimId: string) {
    const claim = await this.prisma.claim.findUnique({ where: { id: claimId } });
    if (!claim) throw new NotFoundException('Claim not found');

    if (claim.status !== ClaimStatus.AI_RESOLVED && claim.status !== ClaimStatus.CHALLENGED) {
      throw new BadRequestException('Claim is not ready for human review');
    }

    return this.prisma.claim.update({
      where: { id: claimId },
      data: { status: ClaimStatus.HUMAN_REVIEW },
    });
  }

  async submitReview(claimId: string, reviewerId: string, decision: string, note?: string) {
    const claim = await this.prisma.claim.findUnique({ where: { id: claimId } });
    if (!claim) throw new NotFoundException('Claim not found');

    if (claim.status !== ClaimStatus.HUMAN_REVIEW) {
      throw new BadRequestException('Claim is not in human review status');
    }

    const review = await this.prisma.humanReview.create({
      data: {
        claimId,
        reviewerId,
        decision,
        note,
      },
    });

    // نهایی کردن claim
    await this.prisma.claim.update({
      where: { id: claimId },
      data: { status: ClaimStatus.FINALIZED },
    });

    return review;
  }

  async getPendingReviews() {
    return this.prisma.claim.findMany({
      where: { status: ClaimStatus.HUMAN_REVIEW },
      include: {
        evidence: true,
        aiResolution: true,
        creator: { select: { id: true, name: true, email: true } },
      },
      orderBy: { updatedAt: 'asc' },
    });
  }
}