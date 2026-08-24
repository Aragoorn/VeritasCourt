import { Controller, Post, Get, Body, Param, UseGuards, Request } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ReviewService } from './review.service';

@Controller('review')
@UseGuards(AuthGuard('jwt'))
export class ReviewController {
  constructor(private reviewService: ReviewService) {}

  @Post(':claimId/request')
  requestReview(@Param('claimId') claimId: string) {
    return this.reviewService.requestHumanReview(claimId);
  }

  @Post(':claimId/submit')
  submit(
    @Param('claimId') claimId: string,
    @Body() body: { decision: string; note?: string },
    @Request() req,
  ) {
    return this.reviewService.submitReview(claimId, req.user.id, body.decision, body.note);
  }

  @Get('pending')
  getPending() {
    return this.reviewService.getPendingReviews();
  }
}