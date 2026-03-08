import urllib.request
import json
import urllib.parse

import os
auth_token = os.environ.get("AUTH_TOKEN", "")  # Set AUTH_TOKEN env variable
ct0 = os.environ.get("CT0", "")                 # Set CT0 env variable

url = 'https://twitter.com/i/api/graphql/HJwEKVCsNmEuCqKMrXGiKg/HomeTimeline'
variables = json.dumps({
    'count': 5,
    'includePromotedContent': False,
    'latestControlAvailable': True,
    'requestContext': 'launch'
})
features = json.dumps({
    'rweb_tipjar_consumption_enabled': True,
    'responsive_web_graphql_exclude_directive_enabled': True,
    'verified_phone_label_enabled': False,
    'creator_subscriptions_tweet_preview_api_enabled': True,
    'responsive_web_graphql_timeline_navigation_enabled': True,
    'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
    'communities_web_enable_tweet_community_results_fetch': True,
    'c9s_tweet_anatomy_moderator_badge_enabled': True,
    'articles_preview_enabled': True,
    'tweetypie_unmention_optimization_enabled': True,
    'responsive_web_edit_tweet_api_enabled': True,
    'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
    'view_counts_everywhere_api_enabled': True,
    'longform_notetweets_consumption_enabled': True,
    'responsive_web_twitter_article_tweet_consumption_enabled': True,
    'tweet_awards_web_tipping_enabled': False,
    'creator_subscriptions_quote_tweet_preview_enabled': False,
    'freedom_of_speech_not_reach_fetch_enabled': True,
    'standardized_nudges_misinfo': True,
    'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
    'rweb_video_timestamps_enabled': True,
    'longform_notetweets_rich_text_read_enabled': True,
    'longform_notetweets_inline_media_enabled': True,
    'responsive_web_enhance_cards_enabled': False
})

full_url = url + '?' + urllib.parse.urlencode({'variables': variables, 'features': features})

req = urllib.request.Request(full_url)
req.add_header('Cookie', f'auth_token={auth_token}; ct0={ct0}')
req.add_header('X-CSRF-Token', ct0)
req.add_header('Authorization', 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I%2FAl93G57Os%3DAAAAAAAAAAAAAAAAAAAAAG2vGmfb5UNFujxwrXX8T0HGRE8bxJ3b5AkrM3')
req.add_header('X-Twitter-Auth-Type', 'OAuth2Session')
req.add_header('X-Twitter-Active-User', 'yes')
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
req.add_header('Accept', 'application/json')
req.add_header('Referer', 'https://twitter.com/home')
req.add_header('Origin', 'https://twitter.com')

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        instructions = data.get('data', {}).get('home', {}).get('home_timeline_upe', {}).get('timeline', {}).get('instructions', [])
        found = 0
        for inst in instructions:
            if inst.get('type') == 'TimelineAddEntries':
                for entry in inst.get('entries', [])[:10]:
                    tweet_result = entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result', {})
                    legacy = tweet_result.get('legacy', {})
                    user = tweet_result.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})
                    text = legacy.get('full_text', '')
                    if text and found < 5:
                        found += 1
                        name = user.get('name', '?')
                        screen = user.get('screen_name', '?')
                        likes = legacy.get('favorite_count', 0)
                        rts = legacy.get('retweet_count', 0)
                        date = legacy.get('created_at', '')
                        print(f'--- {found}. @{screen} ({name})')
                        print(text[:300])
                        print(f'Likes: {likes} | RT: {rts} | {date}')
                        print()
        if found == 0:
            print('No tweets found in response')
            print('Keys:', list(data.keys()))
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f'HTTP {e.code}: {body[:500]}')
except Exception as e:
    print(f'ERROR: {e}')
