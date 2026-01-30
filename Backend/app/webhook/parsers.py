
import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

def parse_webhook(data: dict) -> Optional[dict]:
    """Main webhook parser - detects event type and routes to specific parser"""
    
    if 'ref' in data and 'commits' in data:
        return parse_push(data)
    elif 'pull_request' in data:
        return parse_pull_request(data)
    else:
        logger.warning(f"Unsupported webhook event type: {list(data.keys())[:5]}")
        return None


def parse_push(data: dict) -> Optional[dict]:
    """Parse GitHub push webhook payload"""
    try:
        commits = data.get('commits', [])
        
        if not commits:
            logger.info("Push event with no commits (new branch or tag)")
            
            head_commit = data.get('head_commit')
            if head_commit:
                author = head_commit.get('author', {}).get('name', 'Unknown')
                timestamp = head_commit.get('timestamp', datetime.utcnow().isoformat())
                commit_id = head_commit.get('id', str(uuid4()))
            else:
                author = data.get('pusher', {}).get('name', 'Unknown')
                timestamp = datetime.utcnow().isoformat()
                commit_id = str(uuid4())
        else:
            first_commit = commits[0]
            author = first_commit.get('author', {}).get('name', 'Unknown')
            timestamp = first_commit.get('timestamp', datetime.utcnow().isoformat())
            commit_id = first_commit.get('id', str(uuid4()))
        
        ref = data.get('ref', 'refs/heads/unknown')
        branch = ref.split('/')[-1]
        
        logger.info(f"✅ Parsed PUSH: {author} -> {branch}")
        
        return {
            'request_id': commit_id,
            'author': author,
            'action': 'PUSH',
            'from_branch': branch,
            'to_branch': branch,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error parsing push event: {e}", exc_info=True)
        return None


def parse_pull_request(data: dict) -> Optional[dict]:
    """Parse GitHub pull request webhook payload"""
    try:
        pr = data.get('pull_request', {})
        action = data.get('action', '')
        
        logger.info(f"PR webhook action received: {action}")
        
        if action not in ['opened', 'closed']:
            logger.info(f"⏭️  Skipping PR action '{action}' (only processing 'opened' and 'closed')")
            return None
        
        # Extract PR data
        author = pr.get('user', {}).get('login', 'Unknown')
        from_branch = pr.get('head', {}).get('ref', 'unknown')
        to_branch = pr.get('base', {}).get('ref', 'unknown')
        timestamp = pr.get('created_at', datetime.utcnow().isoformat())
        pr_number = str(pr.get('number', 'unknown'))
        
        if action == 'closed' and pr.get('merged'):
            event_action = 'MERGE'
            logger.info(f"✅ Parsed MERGE: {author} ({from_branch} -> {to_branch})")
        else:
            event_action = 'PULL_REQUEST'
            logger.info(f"✅ Parsed PULL_REQUEST: {author} ({from_branch} -> {to_branch})")
        
        return {
            'request_id': pr_number,
            'author': author,
            'action': event_action,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error parsing pull request: {e}", exc_info=True)
        return None
