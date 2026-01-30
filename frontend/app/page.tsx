'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast, Toaster } from 'sonner';
import { Activity, GitBranch, GitMerge, GitPullRequest, RefreshCw } from 'lucide-react';
// import { EventCard } from '@/components/EventCard';
import { EventCard } from './components/EventCard';
import { WebhookEvent, EventStats } from '@/types/event';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000').replace(/['";\s]/g, '');
const POLL_INTERVAL = 15000;

export default function Home() {
  const [events, setEvents] = useState<WebhookEvent[]>([]);
  const [stats, setStats] = useState<EventStats>({ total: 0, pushes: 0, pullRequests: 0, merges: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calculateStats = (eventList: WebhookEvent[]): EventStats => {
    return {
      total: eventList.length,
      pushes: eventList.filter(e => e.action === 'PUSH').length,
      pullRequests: eventList.filter(e => e.action === 'PULL_REQUEST').length,
      merges: eventList.filter(e => e.action === 'MERGE').length,
    };
  };

const fetchEvents = async (showToast = false) => {
  try {
    setIsPolling(true);
    setError(null);

    const response = await fetch(`${API_BASE_URL}/events`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch events');
    }

    const data: WebhookEvent[] = await response.json();
    
    // Sort by timestamp - newest first
    data.sort((a, b) => {
      const dateA = new Date(a.timestamp).getTime();
      const dateB = new Date(b.timestamp).getTime();
      return dateB - dateA; // Descending order
    });
    
    // Check for new events (compare with current first item)
    if (events.length > 0 && data.length > events.length) {
      const newEvent = data[0]; // Now this is definitely the newest
      toast.success(`New ${newEvent.action} event!`, {
        description: `${newEvent.author} → ${newEvent.to_branch}`,
        duration: 4000,
      });
    }

    setEvents(data);
    setStats(calculateStats(data));
    setLastUpdate(new Date());
    
    if (showToast && data.length === events.length) {
      toast.info('Up to date', { description: 'No new events', duration: 2000 });
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    setError(message);
    toast.error('Connection failed', { 
      description: 'Could not fetch events from backend',
      duration: 3000 
    });
    console.error('Fetch error:', err);
  } finally {
    setIsPolling(false);
    setIsLoading(false);
  }
};


  useEffect(() => {
    fetchEvents();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchEvents();
    }, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [events]);

  const getLastUpdateText = () => {
    if (!lastUpdate) return 'Never';
    const seconds = Math.floor((Date.now() - lastUpdate.getTime()) / 1000);
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    return `${Math.floor(seconds / 60)}m ago`;
  };

  return (
    <div className="min-h-screen bg-black">
      <Toaster position="top-right" theme="dark" />

      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-5xl font-bold text-white mb-2 tracking-tight">
                Webhook Monitor
              </h1>
              <p className="text-gray-400 text-lg">
                Real-time GitHub repository events
              </p>
            </div>
            
            {/* Live indicator */}
            <div className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full border border-white/10">
              <motion.div
                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="w-2 h-2 bg-green-500 rounded-full"
              />
              <span className="text-white text-sm font-medium">Live</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-gray-400" />
                <span className="text-gray-400 text-sm">Total</span>
              </div>
              <motion.p
                key={stats.total}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className="text-4xl font-bold text-white"
              >
                {isLoading ? (
                  <div className="h-10 w-12 bg-white/10 rounded animate-pulse" />
                ) : (
                  stats.total
                )}
              </motion.p>
            </div>

            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="w-5 h-5 text-gray-400" />
                <span className="text-gray-400 text-sm">Pushes</span>
              </div>
              <motion.p
                key={stats.pushes}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className="text-4xl font-bold text-white"
              >
                  {isLoading ? (
                  <div className="h-10 w-12 bg-white/10 rounded animate-pulse" />
                ) : (
                  stats.pushes
                )}
              </motion.p>
            </div>

            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <GitPullRequest className="w-5 h-5 text-gray-400" />
                <span className="text-gray-400 text-sm">Pull Requests</span>
              </div>
              <motion.p
                key={stats.pullRequests}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className="text-4xl font-bold text-white"
              >
              {isLoading ? (
                  <div className="h-10 w-12 bg-white/10 rounded animate-pulse" />
                ) : (
                  stats.pullRequests
                )}
              </motion.p>
            </div>

            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <GitMerge className="w-5 h-5 text-gray-400" />
                <span className="text-gray-400 text-sm">Merges</span>
              </div>
              <motion.p
                key={stats.merges}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className="text-4xl font-bold text-white"
              >
                 {isLoading ? (
                  <div className="h-10 w-12 bg-white/10 rounded animate-pulse" />
                ) : (
                  stats.merges
                )}
              </motion.p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between mt-6 pt-6 border-t border-white/10">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <RefreshCw className={`w-4 h-4 ${isPolling ? 'animate-spin' : ''}`} />
                <span>
                Updated {isLoading ? 'Loading...' : getLastUpdateText()}
                </span>
            </div>
            
            <button
              onClick={() => fetchEvents(true)}
              disabled={isPolling}
              className="px-5 py-2.5 bg-white text-black hover:bg-gray-200 disabled:bg-gray-800 disabled:text-gray-600 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition-all duration-200"
            >
              Refresh
            </button>
          </div>
        </motion.div>

        {/* Timeline */}
        <div className="space-y-3">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white/5 rounded-2xl p-6 border border-white/10 animate-pulse">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-white/10 rounded-xl" />
                    <div className="flex-1 space-y-3">
                      <div className="h-5 bg-white/10 rounded w-24" />
                      <div className="h-6 bg-white/10 rounded w-3/4" />
                      <div className="h-4 bg-white/10 rounded w-1/2" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white/5 rounded-2xl p-12 border border-white/10 text-center"
            >
              <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Connection Error</h3>
              <p className="text-gray-400 mb-6">Make sure Flask backend is running on port 5000</p>
              <button
                onClick={() => fetchEvents(true)}
                className="px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-gray-200 transition-colors"
              >
                Retry
              </button>
            </motion.div>
          ) : events.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white/5 rounded-2xl p-16 border border-white/10 text-center"
            >
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ repeat: Infinity, duration: 3 }}
                className="w-20 h-20 bg-white/10 rounded-2xl flex items-center justify-center mx-auto mb-6"
              >
                <Activity className="w-10 h-10 text-white" />
              </motion.div>
              <h3 className="text-2xl font-semibold text-white mb-3">
                No events yet
              </h3>
              <p className="text-gray-400 max-w-md mx-auto">
                Push to your repository to see webhook events appear here
              </p>
            </motion.div>
          ) : (
            <AnimatePresence mode="popLayout">
              {events.map((event, index) => (
                <EventCard key={event._id} event={event} index={index} />
              ))}
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  );
}
