// 'use client';

// import { motion } from 'framer-motion';
// import { GitBranch, GitMerge, GitPullRequest, Clock } from 'lucide-react';
// import { WebhookEvent } from '@/types/event';
// // import { formatDistanceToNow } from 'date-fns';
// // import formatDistanceToNow from 'date-fns/formatDistanceToNow';

// import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

// interface EventCardProps {
//   event: WebhookEvent;
//   index: number;
// }

// const eventConfig = {
//   PUSH: {
//     icon: GitBranch,
//     gradient: 'from-blue-500 to-cyan-500',
//     bgColor: 'bg-blue-500/10',
//     borderColor: 'border-blue-500/20',
//     label: 'pushed to',
//   },
//   PULL_REQUEST: {
//     icon: GitPullRequest,
//     gradient: 'from-purple-500 to-pink-500',
//     bgColor: 'bg-purple-500/10',
//     borderColor: 'border-purple-500/20',
//     label: 'opened a pull request from',
//   },
//   MERGE: {
//     icon: GitMerge,
//     gradient: 'from-green-500 to-emerald-500',
//     bgColor: 'bg-green-500/10',
//     borderColor: 'border-green-500/20',
//     label: 'merged',
//   },
// };

// export function EventCard({ event, index }: EventCardProps) {
//   const config = eventConfig[event.action];
//   const Icon = config.icon;

//   const formatTimestamp = (timestamp: string) => {
//     try {
//       const date = new Date(timestamp);
//       return {
//         relative: formatDistanceToNow(date, { addSuffix: true }),
//         full: date.toLocaleString('en-US', {
//           month: 'short',
//           day: 'numeric',
//           year: 'numeric',
//           hour: 'numeric',
//           minute: '2-digit',
//           hour12: true,
//         }),
//       };
//     } catch {
//       return { relative: 'Just now', full: timestamp };
//     }
//   };

//   const time = formatTimestamp(event.timestamp);

//   return (
//     <motion.div
//       initial={{ opacity: 0, y: 20 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.4, delay: index * 0.1 }}
//       whileHover={{ y: -4, transition: { duration: 0.2 } }}
//       className="relative group"
//     >
//       {/* Timeline connector */}
//       <div className="absolute left-6 top-14 w-0.5 h-full bg-gradient-to-b from-slate-700 to-transparent" />
      
//       {/* Card */}
//       <div className={`relative glass rounded-2xl p-6 border ${config.borderColor} hover:border-opacity-40 transition-all duration-300`}>
//         {/* Hover glow effect */}
//         <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${config.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
        
//         <div className="relative flex items-start gap-4">
//           {/* Icon */}
//           <motion.div
//             whileHover={{ rotate: 360, scale: 1.1 }}
//             transition={{ duration: 0.6 }}
//             className={`flex-shrink-0 w-12 h-12 rounded-xl ${config.bgColor} flex items-center justify-center border ${config.borderColor}`}
//           >
//             <Icon className={`w-6 h-6 bg-gradient-to-r ${config.gradient} bg-clip-text text-transparent`} />
//           </motion.div>

//           {/* Content */}
//           <div className="flex-1 min-w-0">
//             {/* Action type badge */}
//             <div className="flex items-center gap-2 mb-2">
//               <span className={`px-2.5 py-1 text-xs font-semibold rounded-full bg-gradient-to-r ${config.gradient} text-white`}>
//                 {event.action}
//               </span>
//             </div>

//             {/* Event description */}
//             <p className="text-slate-200 text-base mb-3">
//               <span className="font-semibold text-white">{event.author}</span>
//               {' '}{config.label}{' '}
//               {event.action !== 'PUSH' && (
//                 <>
//                   <code className="px-2 py-0.5 bg-slate-800 rounded text-sm font-mono text-cyan-400">
//                     {event.from_branch}
//                   </code>
//                   {' → '}
//                 </>
//               )}
//               <code className="px-2 py-0.5 bg-slate-800 rounded text-sm font-mono text-emerald-400">
//                 {event.to_branch}
//               </code>
//             </p>

//             {/* Timestamp */}
//             <div className="flex items-center gap-2 text-sm text-slate-400">
//               <Clock className="w-4 h-4" />
//               <span>{time.relative}</span>
//               <span className="text-slate-600">•</span>
//               <span>{time.full}</span>
//             </div>

//             {/* Request ID (subtle) */}
//             <div className="mt-3 pt-3 border-t border-slate-700/50">
//               <p className="text-xs text-slate-500 font-mono">
//                 #{event.request_id.slice(0, 12)}
//               </p>
//             </div>
//           </div>
//         </div>
//       </div>
//     </motion.div>
//   );
// }

'use client';

import { motion } from 'framer-motion';
import { GitBranch, GitMerge, GitPullRequest, Clock } from 'lucide-react';
import { WebhookEvent } from '@/types/event';
// import { formatDistanceToNow } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface EventCardProps {
  event: WebhookEvent;
  index: number;
}

const eventConfig = {
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
  const config = eventConfig[event.action];
  const Icon = config.icon;

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
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
        {/* Icon */}
        <div className="flex-shrink-0 w-12 h-12 bg-white rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
          <Icon className="w-6 h-6 text-black" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Action badge */}
          <div className="inline-block px-3 py-1 bg-white/10 rounded-full mb-3">
            <span className="text-xs font-semibold text-white uppercase tracking-wide">
              {event.action}
            </span>
          </div>

          {/* Description */}
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

          {/* Timestamp */}
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
