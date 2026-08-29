import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createClient, createAccount } from 'genlayer-js';

@Injectable()
export class GenlayerService {
  private client: any;
  private readonly logger = new Logger(GenlayerService.name);
  private contractAddress: string;

  constructor(private config: ConfigService) {
    this.contractAddress = this.config.get('GENLAYER_CONTRACT_ADDRESS') || '';
    const account = createAccount();

    // جلوگیری از خطای moduleResolution
    const { studionet } = require('genlayer-js/chains');

    this.client = createClient({
      chain: studionet,
      account,
    });
  }

  private async waitFinalized(hash: string, retries = 100) {
    const { TransactionStatus } = require('genlayer-js/types');
    return this.client.waitForTransactionReceipt({
      hash,
      status: TransactionStatus.FINALIZED,
      retries,
      interval: 3000,
    });
  }

  async createClaim(params: {
    externalId: string;
    title: string;
    description: string;
    evidenceUrls?: string;
    plaintiff?: string;
    defendant?: string;
    templateId?: string;
    jurisdiction?: string;
    evidenceHashesJson?: string;
    callbackContract?: string;
    beneficiary?: string;
    value?: bigint;
  }) {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'create_claim',
        args: [
          params.externalId,
          params.title,
          params.description,
          params.evidenceUrls || '',
          params.plaintiff || '',
          params.defendant || '0x0000000000000000000000000000000000000001',
          params.templateId || 'general',
          params.jurisdiction || '',
          params.evidenceHashesJson || '[]',
          params.callbackContract || '',
          params.beneficiary || '',
        ],
        value: params.value || 0n,
      });

      await this.waitFinalized(hash);

      const count = await this.client.readContract({
        address: this.contractAddress,
        functionName: 'get_claim_count',
        args: [],
      });

      return {
        success: true,
        claimId: String(Number(count) - 1),
        txHash: hash,
      };
    } catch (error) {
      this.logger.error('createClaim error', error);
      throw error;
    }
  }

  async addEvidence(claimId: string, extraUrls: string, hashesJson = '') {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'add_evidence',
        args: [BigInt(claimId), extraUrls, hashesJson],
        value: 0n,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash };
    } catch (error) {
      this.logger.error('addEvidence error', error);
      throw error;
    }
  }

  async resolveClaim(claimId: string) {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'resolve_claim',
        args: [BigInt(claimId)],
        value: 0n,
      });
      await this.waitFinalized(hash, 120);

      const resolution = await this.getResolution(claimId);
      return { success: true, resolution, txHash: hash };
    } catch (error) {
      this.logger.error('resolveClaim error', error);
      throw error;
    }
  }

  async challengeClaim(claimId: string, reason: string, value: bigint | string = 0n) {
    try {
      const txValue = typeof value === 'string' ? BigInt(value) : value;

      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'challenge',
        args: [BigInt(claimId), reason],
        value: txValue,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash };
    } catch (error) {
      this.logger.error('challengeClaim error', error);
      throw error;
    }
  }

  async appealClaim(claimId: string, reason: string, value: bigint | string = 0n) {
    try {
      const txValue = typeof value === 'string' ? BigInt(value) : value;

      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'appeal',
        args: [BigInt(claimId), reason],
        value: txValue,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash };
    } catch (error) {
      this.logger.error('appealClaim error', error);
      throw error;
    }
  }

  async castHumanVote(claimId: string, vote: string) {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'cast_human_vote',
        args: [BigInt(claimId), vote.toUpperCase()],
        value: 0n,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash };
    } catch (error) {
      this.logger.error('castHumanVote error', error);
      throw error;
    }
  }

  async finalizeClaim(claimId: string) {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'finalize_claim',
        args: [BigInt(claimId)],
        value: 0n,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash, on_chain: true };
    } catch (error) {
      this.logger.error('finalizeClaim error', error);
      throw error;
    }
  }

  async setAppointedResolver(resolver: string, endpoint: string) {
    try {
      const hash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: 'set_appointed_resolver',
        args: [resolver, endpoint],
        value: 0n,
      });
      await this.waitFinalized(hash);
      return { success: true, txHash: hash };
    } catch (error) {
      this.logger.error('setAppointedResolver error', error);
      throw error;
    }
  }

  // ==================== View Methods ====================

  async getClaim(claimId: string) {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_claim',
      args: [BigInt(claimId)],
    });
    return typeof result === 'string' ? JSON.parse(result || '{}') : result;
  }

  async getResolution(claimId: string) {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_resolution',
      args: [BigInt(claimId)],
    });
    return typeof result === 'string' ? JSON.parse(result || '{}') : result;
  }

  async getHistory(claimId: string) {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_history',
      args: [BigInt(claimId)],
    });
    return typeof result === 'string' ? JSON.parse(result || '[]') : result;
  }

  async getHumanVotes(claimId: string) {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_human_votes',
      args: [BigInt(claimId)],
    });
    return typeof result === 'string' ? JSON.parse(result || '[]') : result;
  }

  async getAppointedResolver() {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_appointed_resolver',
      args: [],
    });
    return typeof result === 'string' ? JSON.parse(result || '{}') : result;
  }

  async getAuditTrail(claimId: string) {
    const result = await this.client.readContract({
      address: this.contractAddress,
      functionName: 'get_audit_trail',
      args: [BigInt(claimId)],
    });
    return typeof result === 'string' ? JSON.parse(result || '{}') : result;
  }
}
