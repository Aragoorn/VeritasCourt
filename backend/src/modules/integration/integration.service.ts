import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { NotificationService } from '../notification/notification.service';

@Injectable()
export class IntegrationService {
  private readonly logger = new Logger(IntegrationService.name);

  constructor(
    private prisma: PrismaService,
    private notification: NotificationService,
  ) {}

  async triggerWebhookForCompany(companyId: string, event: string, payload: any) {
    const company = await this.prisma.company.findUnique({
      where: { id: companyId },
    });

    if (!company?.webhookUrl) {
      this.logger.warn(`No webhook configured for company ${companyId}`);
      return { success: false, reason: 'No webhook URL' };
    }

    return this.notification.sendWebhook(company.webhookUrl, {
      event,
      timestamp: new Date().toISOString(),
      data: payload,
    });
  }

  async getCompanyByApiKey(apiKey: string) {
    return this.prisma.company.findUnique({
      where: { apiKey },
    });
  }
}