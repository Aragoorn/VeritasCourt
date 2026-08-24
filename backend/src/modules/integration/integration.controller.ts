import { Controller, Get, Headers, UnauthorizedException } from '@nestjs/common';
import { IntegrationService } from './integration.service';

@Controller('integration')
export class IntegrationController {
  constructor(private integrationService: IntegrationService) {}

  // مثال: دریافت اطلاعات شرکت با API Key (برای سیستم‌های خارجی)
  @Get('me')
  async getCompany(@Headers('x-api-key') apiKey: string) {
    if (!apiKey) throw new UnauthorizedException('API Key required');

    const company = await this.integrationService.getCompanyByApiKey(apiKey);
    if (!company) throw new UnauthorizedException('Invalid API Key');

    return {
      id: company.id,
      name: company.name,
      webhookUrl: company.webhookUrl,
    };
  }
}