import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class NotificationService {
  private readonly logger = new Logger(NotificationService.name);

  async sendClaimStatusUpdate(email: string, claimId: string, status: string) {
    // فعلاً فقط لاگ می‌کنیم. بعداً می‌توان به SendGrid / Resend / Slack وصل کرد
    this.logger.log(`[Notification] Claim ${claimId} status changed to ${status} → ${email}`);
    return { success: true };
  }

  async sendHumanReviewRequest(reviewerEmail: string, claimId: string) {
    this.logger.log(`[Notification] Human review requested for claim ${claimId} → ${reviewerEmail}`);
    return { success: true };
  }

  async sendWebhook(webhookUrl: string, payload: any) {
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return { success: response.ok };
    } catch (error) {
      this.logger.error('Webhook failed', error);
      return { success: false };
    }
  }
}