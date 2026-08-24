import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { NotificationService } from './notification.service';

@Controller('notification')
@UseGuards(AuthGuard('jwt'))
export class NotificationController {
  constructor(private notificationService: NotificationService) {}

  @Post('test')
  test(@Body() body: { email: string; claimId: string; status: string }) {
    return this.notificationService.sendClaimStatusUpdate(
      body.email,
      body.claimId,
      body.status,
    );
  }
}