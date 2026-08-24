import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  UseGuards,
  Request,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ClaimsService } from './claims.service';
import { CreateClaimDto } from './dto/create-claim.dto';

@Controller('claims')
@UseGuards(AuthGuard('jwt'))
export class ClaimsController {
  constructor(private claimsService: ClaimsService) {}

  @Post()
  create(@Body() dto: CreateClaimDto, @Request() req) {
    return this.claimsService.create(
      dto,
      req.user.id,
      req.user.companyId || 'default',
    );
  }

  @Get()
  findAll(@Request() req) {
    return this.claimsService.findAll(req.user.companyId);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.claimsService.findOne(id);
  }

  @Post(':id/resolve')
  resolve(@Param('id') id: string) {
    return this.claimsService.resolve(id);
  }

  @Post(':id/challenge')
  challenge(@Param('id') id: string, @Body() body: { reason: string }) {
    return this.claimsService.challenge(id, body.reason);
  }

  @Post(':id/appeal')
  appeal(@Param('id') id: string, @Body() body: { reason: string }) {
    return this.claimsService.appeal(id, body.reason);
  }

  @Post(':id/finalize')
  finalize(@Param('id') id: string) {
    return this.claimsService.finalize(id);
  }
}