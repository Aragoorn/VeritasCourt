import { Module } from '@nestjs/common';
import { IntegrationService } from './integration.service';
import { IntegrationController } from './integration.controller';
import { NotificationModule } from '../notification/notification.module';

@Module({
  imports: [NotificationModule],
  providers: [IntegrationService],
  controllers: [IntegrationController],
  exports: [IntegrationService],
})
export class IntegrationModule {}