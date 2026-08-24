import { Controller, Post, Get, Body, Param, UseGuards, Request } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { EvidenceService } from './evidence.service';

@Controller('evidence')
@UseGuards(AuthGuard('jwt'))
export class EvidenceController {
  constructor(private evidenceService: EvidenceService) {}

  @Post(':claimId')
  add(
    @Param('claimId') claimId: string,
    @Body() body: { url: string; fileName?: string; mimeType?: string },
    @Request() req,
  ) {
    return this.evidenceService.addEvidence(claimId, {
      ...body,
      uploadedBy: req.user.id,
    });
  }

  @Get('claim/:claimId')
  findByClaim(@Param('claimId') claimId: string) {
    return this.evidenceService.findByClaim(claimId);
  }
}