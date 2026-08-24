import { IsString, IsOptional, MinLength, MaxLength } from 'class-validator';

export class CreateClaimDto {
  @IsString()
  @MinLength(5)
  @MaxLength(180)
  title: string;

  @IsString()
  @MinLength(20)
  @MaxLength(3000)
  description: string;

  @IsString()
  @IsOptional()
  externalId?: string;

  @IsString()
  @IsOptional()
  evidenceUrls?: string;

  @IsString()
  @IsOptional()
  plaintiff?: string;

  @IsString()
  @IsOptional()
  defendant?: string;

  @IsString()
  @IsOptional()
  templateId?: string;

  @IsString()
  @IsOptional()
  jurisdiction?: string;
}