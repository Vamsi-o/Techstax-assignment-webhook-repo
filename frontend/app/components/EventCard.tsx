
'use client';

import { motion } from 'framer-motion';
import { GitBranch, GitMerge, GitPullRequest, Clock, GitCommit } from 'lucide-react';
import { WebhookEvent } from '@/types/event';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface EventCardProps {
  event: WebhookEvent;
  index: number;
}

const defaultEventConfig = {
  icon: GitCommit,
  label: 'performed action on',
};

const eventConfig: Record<string, { icon: typeof GitCommit; label: string }> = {
  PUSH: {
    icon: GitBranch,
    label: 'pushed to',
  },
  PULL_REQUEST: {
    icon: GitPullRequest,
    label: 'opened pull request from',
  },
  MERGE: {
    icon: GitMerge,
    label: 'merged',
  },
};

export function EventCard({ event, index }: EventCardProps) {
  const config = eventConfig[event.action] ?? defaultEventConfig;
  const Icon = config.icon;

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      return { relative: 'Just now', full: timestamp };
    }
    try {
      return {
        relative: formatDistanceToNow(date, { addSuffix: true }),
        full: date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
        }),
      };
    } catch {
      return { relative: 'Just now', full: timestamp };
    }
  };

  const time = formatTimestamp(event.timestamp);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ scale: 1.01, transition: { duration: 0.2 } }}
      className="bg-white/5 rounded-2xl p-6 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-200 group"
    >
      <div className="flex items-start gap-5">
        <div className="flex-shrink-0 w-12 h-12 bg-white rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
          <Icon className="w-6 h-6 text-black" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="inline-block px-3 py-1 bg-white/10 rounded-full mb-3">
            <span className="text-xs font-semibold text-white uppercase tracking-wide">
              {event.action}
            </span>
          </div>

          <p className="text-white text-lg mb-3 leading-relaxed">
            <span className="font-semibold">{event.author}</span>
            {' '}{config.label}{' '}
            {event.action !== 'PUSH' && (
              <>
                <code className="px-2 py-1 bg-white/10 rounded text-sm font-mono">
                  {event.from_branch}
                </code>
                {' → '}
              </>
            )}
            <code className="px-2 py-1 bg-white/10 rounded text-sm font-mono">
              {event.to_branch}
            </code>
          </p>

          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Clock className="w-4 h-4" />
            <span>{time.relative}</span>
            <span>•</span>
            <span>{time.full}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
