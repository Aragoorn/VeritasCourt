import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class EvidenceService {
  constructor(private prisma: PrismaService) {}

  async addEvidence(claimId: string, data: {
    url: string;
    fileName?: string;
    mimeType?: string;
    uploadedBy: string;
    ipfsHash?: string;
  }) {
    const claim = await this.prisma.claim.findUnique({ where: { id: claimId } });
    if (!claim) throw new NotFoundException('Claim not found');

    return this.prisma.evidence.create({
      data: {
        claimId,
        url: data.url,
        fileName: data.fileName,
        mimeType: data.mimeType,
        uploadedBy: data.uploadedBy,
        ipfsHash: data.ipfsHash,
      },
    });
  }

  async findByClaim(claimId: string) {
    return this.prisma.evidence.findMany({
      where: { claimId },
      orderBy: { createdAt: 'asc' },
    });
  }

  async remove(id: string) {
    return this.prisma.evidence.delete({ where: { id } });
  }
}