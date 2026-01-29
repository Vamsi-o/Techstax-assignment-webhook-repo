export type EventAction = 'PUSH' | 'PULL_REQUEST' | 'MERGE';

export interface WebhookEvent {
  _id: string;
  request_id: string;
  author: string;
  action: EventAction;
  from_branch: string;
  to_branch: string;
  timestamp: string;
}

export interface EventStats {
  total: number;
  pushes: number;
  pullRequests: number;
  merges: number;
}
