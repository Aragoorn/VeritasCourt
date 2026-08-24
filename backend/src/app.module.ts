import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_FILTER } from '@nestjs/core';
import { configuration } from './config';
import { AllExceptionsFilter } from './common/filters/http-exception.filter';

import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { ClaimsModule } from './modules/claims/claims.module';
import { EvidenceModule } from './modules/evidence/evidence.module';
import { ReviewModule } from './modules/review/review.module';
import { GenlayerModule } from './modules/genlayer/genlayer.module';
import { NotificationModule } from './modules/notification/notification.module';
import { IntegrationModule } from './modules/integration/integration.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    PrismaModule,
    AuthModule,
    UsersModule,
    ClaimsModule,
    EvidenceModule,
    ReviewModule,
    GenlayerModule,
    NotificationModule,
    IntegrationModule,
  ],
  providers: [
    {
      provide: APP_FILTER,
      useClass: AllExceptionsFilter,
    },
  ],
})
export class AppModule {}