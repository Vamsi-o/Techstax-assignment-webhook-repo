import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

def parse_webhook(data: dict) -> Optional[dict]:
    """Main webhook parser - detects event type and routes to specific parser"""
    
    # Detect event type
    if 'ref' in data and 'commits' in data:
        return parse_push(data)
    elif 'pull_request' in data:
        return parse_pull_request(data)
    else:
        logger.warning(f"Unsupported webhook event type: {list(data.keys())}")
        return None


def parse_push(data: dict) -> Optional[dict]:
    """Parse GitHub push webhook payload"""
    try:
        commits = data.get('commits', [])
        if not commits:
            logger.warning("Push event with no commits")
            return None
        
        first_commit = commits[0]
        author = first_commit.get('author', {}).get('name', 'Unknown')
        ref = data.get('ref', 'refs/heads/unknown')
        branch = ref.split('/')[-1]
        timestamp = first_commit.get('timestamp', datetime.utcnow().isoformat())
        commit_id = first_commit.get('id', str(uuid4()))
        
        logger.info(f"Parsed PUSH: {author} -> {branch}")
        
        return {
            'request_id': commit_id,
            'author': author,
            'action': 'PUSH',
            'from_branch': branch,
            'to_branch': branch,
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Error parsing push event: {e}", exc_info=True)
        return None


def parse_pull_request(data: dict) -> Optional[dict]:
    """Parse GitHub pull request webhook payload"""
    try:
        pr = data.get('pull_request', {})
        action = data.get('action', '')
        
        # Only process 'opened' and 'closed' actions
        if action not in ['opened', 'closed']:
            logger.debug(f"Skipping PR action: {action}")
            return None
        
        author = pr.get('user', {}).get('login', 'Unknown')
        from_branch = pr.get('head', {}).get('ref', 'unknown')
        to_branch = pr.get('base', {}).get('ref', 'unknown')
        timestamp = pr.get('created_at', datetime.utcnow().isoformat())
        pr_number = str(pr.get('number', 'unknown'))
        
        # Check if PR was merged
        if action == 'closed' and pr.get('merged'):
            event_action = 'MERGE'
            logger.info(f"Parsed MERGE: {author} ({from_branch} -> {to_branch})")
        else:
            event_action = 'PULL_REQUEST'
            logger.info(f"Parsed PULL_REQUEST: {author} ({from_branch} -> {to_branch})")
        
        return {
            'request_id': pr_number,
            'author': author,
            'action': event_action,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except Exception as e:
        logger.error(f"Error parsing pull request: {e}", exc_info=True)
        return None
