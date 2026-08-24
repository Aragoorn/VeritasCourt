import { Module } from '@nestjs/common';
import { GenlayerService } from './genlayer.service';

@Module({
  providers: [GenlayerService],
  exports: [GenlayerService],
})
export class GenlayerModule {}