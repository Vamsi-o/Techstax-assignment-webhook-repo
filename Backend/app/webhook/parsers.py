"""
GitHub webhook payload parsers

This file contains functions to parse different GitHub event types:
1. PUSH events (when someone pushes code)
2. PULL_REQUEST events (when someone creates a PR)
3. MERGE events (when a PR is merged)
"""

# Fix imports when running directly
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def parse_push_event(data):
    """
    Parse GitHub PUSH webhook payload
    
    GitHub PUSH payload structure:
    {
        "ref": "refs/heads/main",
        "commits": [{
            "id": "abc123...",
            "author": {"name": "Vamshi"},
            "timestamp": "2026-01-29T06:30:00Z"
        }]
    }
    
    Args:
        data: GitHub webhook JSON payload
    
    Returns:
        dict: Parsed event data with schema:
            {
                'request_id': commit hash,
                'author': author name,
                'action': 'PUSH',
                'from_branch': branch name,
                'to_branch': branch name,
                'timestamp': ISO timestamp
            }
        None: If parsing fails
    """
    try:
        # Check if commits array exists and has data
        # Why? Some push events might be empty (branch deletion)
        if not data.get('commits') or len(data['commits']) == 0:
            print("⚠️  PUSH event has no commits")
            return None
        
        # Get first commit from the array
        # Why first? Assignment only asks for one event per push
        commit = data['commits'][0]
        
        # Extract branch name from ref
        # ref format: "refs/heads/main" or "refs/heads/feature-branch"
        # We only want the last part: "main" or "feature-branch"
        ref = data.get('ref', '')
        branch = ref.split('/')[-1] if '/' in ref else ref
        
        # Build the event data according to assignment schema
        event_data = {
            'request_id': commit['id'],              # Commit hash
            'author': commit['author']['name'],      # Author's name
            'action': 'PUSH',                        # Event type
            'from_branch': branch,                   # Same for push
            'to_branch': branch,                     # Same for push
            'timestamp': commit['timestamp']         # ISO 8601 format
        }
        
        print(f"✅ Parsed PUSH: {event_data['author']} -> {branch}")
        return event_data
        
    except KeyError as e:
        # KeyError = required field is missing from JSON
        # Example: commit['author'] doesn't exist
        print(f"❌ Missing field in PUSH event: {e}")
        return None
        
    except IndexError as e:
        # IndexError = array access failed
        # Example: data['commits'][0] but commits is empty
        print(f"❌ Invalid PUSH structure: {e}")
        return None
        
    except Exception as e:
        # Catch any other unexpected errors
        print(f"❌ Unexpected error parsing PUSH: {e}")
        return None


def parse_pull_request_event(data):
    """
    Parse GitHub PULL_REQUEST webhook payload
    
    Handles both:
    - PULL_REQUEST events (PR created/opened)
    - MERGE events (PR closed + merged)
    
    GitHub PR payload structure:
    {
        "action": "opened" or "closed",
        "pull_request": {
            "id": 12345,
            "user": {"login": "vamsi"},
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "merged": true/false,
            "created_at": "2026-01-29T06:30:00Z",
            "merged_at": "2026-01-29T07:00:00Z"
        }
    }
    
    Args:
        data: GitHub webhook JSON payload
    
    Returns:
        dict: Parsed event with action='PULL_REQUEST' or 'MERGE'
        None: If parsing fails
    """
    try:
        # Get pull_request object
        pr = data['pull_request']
        
        # Get the action type (opened, closed, synchronize, etc.)
        action_type = data['action']
        
        # Determine if this is a MERGE event
        # MERGE = action is 'closed' AND merged flag is True
        # Why? GitHub doesn't send separate "merge" event
        # It sends PR closed event with merged=true
        is_merge = action_type == 'closed' and pr.get('merged', False)
        
        if is_merge:
            # This is a MERGE
            event_action = 'MERGE'
            # Use merged_at timestamp if available, otherwise updated_at
            timestamp = pr.get('merged_at', pr.get('updated_at', pr['created_at']))
        else:
            # This is a regular PULL_REQUEST
            event_action = 'PULL_REQUEST'
            # Use created_at for when PR was opened
            timestamp = pr['created_at']
        
        # Build event data according to assignment schema
        event_data = {
            'request_id': str(pr['id']),        # PR ID (convert to string)
            'author': pr['user']['login'],       # GitHub username
            'action': event_action,              # PULL_REQUEST or MERGE
            'from_branch': pr['head']['ref'],    # Source branch (where changes are)
            'to_branch': pr['base']['ref'],      # Target branch (where merging to)
            'timestamp': timestamp               # ISO 8601 format
        }
        
        print(f"✅ Parsed {event_action}: {event_data['author']} ({event_data['from_branch']} -> {event_data['to_branch']})")
        return event_data
        
    except KeyError as e:
        # Missing required field in PR JSON
        print(f"❌ Missing field in PR event: {e}")
        return None
        
    except Exception as e:
        # Any other unexpected error
        print(f"❌ Unexpected error parsing PR: {e}")
        return None


def parse_webhook(data):
    """
    Main webhook parser - routes to appropriate parser
    
    Determines event type by checking which top-level keys exist:
    - Has 'commits' key? -> PUSH event
    - Has 'pull_request' key? -> PR or MERGE event
    - Neither? -> Unsupported event type
    
    Args:
        data: GitHub webhook JSON payload
    
    Returns:
        dict: Parsed event data
        None: If unsupported or parsing failed
    """
    # Check for PUSH event
    # GitHub PUSH webhooks have a 'commits' array
    if 'commits' in data and data.get('commits'):
        return parse_push_event(data)
    
    # Check for PULL_REQUEST event
    # GitHub PR webhooks have a 'pull_request' object
    elif 'pull_request' in data:
        return parse_pull_request_event(data)
    
    # Unsupported event type
    else:
        print("⚠️  Unsupported webhook event type")
        return None


# ============ TEST CODE ============
# Only runs when you execute this file directly
# python3 app/webhook/parsers.py

if __name__ == '__main__':
    print("=" * 60)
    print("TESTING WEBHOOK PARSERS")
    print("=" * 60)
    
    # Test 1: PUSH event
    print("\n[TEST 1] PUSH Event")
    print("-" * 60)
    push_data = {
        'ref': 'refs/heads/main',
        'commits': [{
            'id': 'abc123def456',
            'author': {'name': 'Vamshi'},
            'timestamp': '2026-01-29T06:30:00Z'
        }]
    }
    
    result = parse_push_event(push_data)
    if result:
        print(f"✅ PUSH parsed successfully:")
        print(f"   Author: {result['author']}")
        print(f"   Branch: {result['to_branch']}")
        print(f"   Action: {result['action']}")
    else:
        print("❌ PUSH parsing failed")
    
    # Test 2: PULL_REQUEST event
    print("\n[TEST 2] PULL_REQUEST Event")
    print("-" * 60)
    pr_data = {
        'action': 'opened',
        'pull_request': {
            'id': 12345,
            'user': {'login': 'vamsi'},
            'head': {'ref': 'feature-branch'},
            'base': {'ref': 'main'},
            'created_at': '2026-01-29T06:30:00Z',
            'merged': False
        }
    }
    
    result = parse_pull_request_event(pr_data)
    if result:
        print(f"✅ PULL_REQUEST parsed successfully:")
        print(f"   Author: {result['author']}")
        print(f"   From: {result['from_branch']} -> To: {result['to_branch']}")
        print(f"   Action: {result['action']}")
    else:
        print("❌ PULL_REQUEST parsing failed")
    
    # Test 3: MERGE event
    print("\n[TEST 3] MERGE Event")
    print("-" * 60)
    merge_data = {
        'action': 'closed',
        'pull_request': {
            'id': 12345,
            'user': {'login': 'vamsi'},
            'head': {'ref': 'feature-branch'},
            'base': {'ref': 'main'},
            'created_at': '2026-01-29T06:30:00Z',
            'merged': True,
            'merged_at': '2026-01-29T07:00:00Z'
        }
    }
    
    result = parse_pull_request_event(merge_data)
    if result:
        print(f"✅ MERGE parsed successfully:")
        print(f"   Author: {result['author']}")
        print(f"   From: {result['from_branch']} -> To: {result['to_branch']}")
        print(f"   Action: {result['action']}")
    else:
        print("❌ MERGE parsing failed")
    
    # Test 4: parse_webhook() main function
    print("\n[TEST 4] Main parse_webhook() Function")
    print("-" * 60)
    
    # Test with PUSH
    result = parse_webhook(push_data)
    print(f"PUSH via parse_webhook(): {result['action'] if result else 'FAILED'}")
    
    # Test with PR
    result = parse_webhook(pr_data)
    print(f"PR via parse_webhook(): {result['action'] if result else 'FAILED'}")
    
    # Test with MERGE
    result = parse_webhook(merge_data)
    print(f"MERGE via parse_webhook(): {result['action'] if result else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("✅ ALL PARSER TESTS COMPLETE")
    print("=" * 60)
