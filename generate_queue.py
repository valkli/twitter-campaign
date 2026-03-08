"""
Генерирует tweet_queue.json из twitter_complete_90tweets.md
Дни 6-30, начиная с 2026-03-07
"""
import json
from datetime import datetime, timedelta, timezone

# Все твиты дней 6-30 (в порядке появления в файле)
tweets_raw = [
    # DAY 6
    {"day": 6, "slot": 1, "topic": "LEADGEN", "text": "Your pipeline is a LEAKY BUCKET. Spend $10k on ads, lose 70% to poor follow-up. Spend $2k on ads + $8k on AI automation = 40% loss rate. The ROI delta is INSANE. #marketing #sales"},
    {"day": 6, "slot": 2, "topic": "SPAIN",   "text": "Foreign investment in Spain is UP 45% YoY. Institutional capital is POURING IN. If you're still hesitant—you're leaving 6-7 figure gains on the table every quarter. #marketdata #wealth"},
    {"day": 6, "slot": 3, "topic": "AI",      "text": "Most people use AI to save time. Winners use AI to do things that were previously IMPOSSIBLE. Personalizing 10,000 emails isn't \"saving time\"—it's a new capability. #innovation #scale"},
    # DAY 7
    {"day": 7, "slot": 1, "topic": "LEADGEN", "text": "TRUTH: The sales teams winning right now aren't smarter. They're just automated 3 levels deeper than their competitors. If you're not automating lead gen—you've already lost. #salesops #business"},
    {"day": 7, "slot": 2, "topic": "SPAIN",   "text": "Spanish mortgage rates? Still 40% lower than Germany. Population growing in key cities. This is STRUCTURAL value. Not a bubble. Not hype. Market fundamentals are STRONG. #economics #investing"},
    {"day": 7, "slot": 3, "topic": "AI",      "text": "ChatGPT as your personal coach: \"Here's my sales call recording. Rate my performance.\" It gives you BRUTAL feedback. You improve. Repeat 30 days straight = 10x better closer. #growth #sales"},
    # DAY 8
    {"day": 8, "slot": 1, "topic": "LEADGEN", "text": "\"Is cold outreach spam?\" Only if it's irrelevant. AI makes it relevant at scale. We analyze a prospect's entire footprint to send ONE perfect message. That's not spam. That's value. #b2b #outreach"},
    {"day": 8, "slot": 2, "topic": "SPAIN",   "text": "Don't fear Spanish bureaucracy. Automate it. Lawyers + Gestors + Digital Signatures. Once you crack the system, the barrier to entry protects your profits. #business #spain"},
    {"day": 8, "slot": 3, "topic": "AI",      "text": "The skill of 2026 isn't \"coding.\" It's \"orchestrating.\" Can you make Claude talk to Midjourney talk to Zapier? The Architects are the new Developers. #nocode #futureofwork"},
    # DAY 9
    {"day": 9, "slot": 1, "topic": "LEADGEN", "text": "Stop chasing \"more leads.\" Chase \"faster response.\" 78% of deals go to the first responder. AI responds in 4 seconds. Humans respond in 4 hours. Do the math. #speed #winning"},
    {"day": 9, "slot": 2, "topic": "SPAIN",   "text": "Lifestyle dividend: ROI isn't just money. It's waking up in a Mediterranean climate, eating fresh food, living safely. Spain pays you in cashflow AND life quality. #lifestyle #freedom"},
    {"day": 9, "slot": 3, "topic": "AI",      "text": "ChatGPT → Canva → LinkedIn automation = 30 posts/month designed, written, scheduled. You do it once. Results compound for 90 days. That's LEVERAGE at scale. #content #marketing"},
    # DAY 10
    {"day": 10, "slot": 1, "topic": "LEADGEN", "text": "We built a scraper that finds every new real estate listing in Spain instantly. Then AI contacts the agent. We see deals 48 hours before the market. Technology is an unfair advantage. #proptech #hacking"},
    {"day": 10, "slot": 2, "topic": "SPAIN",   "text": "Valencia vs. Madrid: Madrid gives you status. Valencia gives you ROI. Madrid is peaked. Valencia is ascending. Follow the growth, not the crowd. #investing #tips"},
    {"day": 10, "slot": 3, "topic": "AI",      "text": "Learned Zapier in 2 days. Now 10 of my processes run 100% automatically. No more manual work. Just optimization. That's the shift happening in 2026. #automation #efficiency"},
    # DAY 11
    {"day": 11, "slot": 1, "topic": "LEADGEN", "text": "Marketing agencies are dying. \"AI Growth Partners\" are rising. You don't need a retainer for SEO. You need a partner who builds SYSTEMS that print leads forever. #agency #change"},
    {"day": 11, "slot": 2, "topic": "SPAIN",   "text": "Buy Spain, hold 10 years, retire early. That's the play. Markets cycle. You catch the bottom (now), sell the top (2027-28). Generational wealth opportunity. #investing #fire"},
    {"day": 11, "slot": 3, "topic": "AI",      "text": "Stop fearing AI will replace you. Fear the person using AI who will replace you. The tool is neutral. The user is the variable. Be the power user. #career #mindset"},
    # DAY 12
    {"day": 12, "slot": 1, "topic": "LEADGEN", "text": "Case study: Real estate agent manually DMs 20 people/day. Gets 1 lead. Our bot DMs 500/day. Gets 25 leads. Cost is same. Who wins the market in 6 months? #realestate #math"},
    {"day": 12, "slot": 2, "topic": "SPAIN",   "text": "Spain's Digital Nomad Visa is bringing high-income tech workers. They need high-quality rentals. They pay premiums. This is the new tenant class you want. #rental #strategy"},
    {"day": 12, "slot": 3, "topic": "AI",      "text": "Generated 200 social media posts using AI this month. Value: €8000 (market rate). Cost: €20 (ChatGPT). Margin: 99.75%. That's leverage. #AI #marketing"},
    # DAY 13
    {"day": 13, "slot": 1, "topic": "LEADGEN", "text": "Your lead qualification process takes 30 minutes per prospect. GenAIx does 100 in 60 seconds. You're literally throwing away 99.7% productivity because you haven't switched. #efficiency #waste"},
    {"day": 13, "slot": 2, "topic": "SPAIN",   "text": "The \"Manana\" culture in Spain is a myth in business. Top circles move FAST. If you think it's slow, you're in the wrong rooms. Upgrade your network. #culture #business"},
    {"day": 13, "slot": 3, "topic": "AI",      "text": "AI doesn't hallucinate. It brainstorms. If you treat it like a search engine, it fails. If you treat it like a creative partner, it's genius. Adjust your expectations. #creativity #llm"},
    # DAY 14
    {"day": 14, "slot": 1, "topic": "LEADGEN", "text": "Building a list used to cost $1 per lead. With AI scraping + enrichment, it costs $0.01. The cost of data has collapsed. The value of ACTION has skyrocketed. #data #strategy"},
    {"day": 14, "slot": 2, "topic": "SPAIN",   "text": "Look at commercial real estate in Alicante. Retail to residential conversions. High complexity, massive margin. This is where the 20% yields are hiding. #development #cre"},
    {"day": 14, "slot": 3, "topic": "AI",      "text": "Pro tip: Paste your codebase into Claude. Ask \"Where are the security vulnerabilities?\" It finds 3 critical bugs in 10 seconds. You just saved a $50k audit. #coding #security"},
    # DAY 15
    {"day": 15, "slot": 1, "topic": "LEADGEN", "text": "Prediction: In 2 years, manual B2B prospecting will be considered \"artisanal\" (and expensive/rare). Automated prospecting will be the standard utility. Adapt now. #future #predictions"},
    {"day": 15, "slot": 2, "topic": "SPAIN",   "text": "Investing in Spain without a local partner is gambling. You need boots on the ground. Someone to check the plumbing, the neighbors, the paperwork. I am that partner. #partnership #trust"},
    {"day": 15, "slot": 3, "topic": "AI",      "text": "Content calendar for 90 days generated by AI in 1 hour. Would've taken me 20 hours. Recovered 19 hours. Multiply by 12 months. I gain 228 hours/year. #AI #time"},
    # DAY 16
    {"day": 16, "slot": 1, "topic": "LEADGEN", "text": "Your automation stack in 2026 = your competitive moat in 2027. Build NOW while everyone's still sleeping. By then? You'll own your entire market category. #strategy #moat"},
    {"day": 16, "slot": 2, "topic": "SPAIN",   "text": "Seville is undervalued. High speed train to Madrid (2.5h). Huge tourism. Beautiful architecture. Prices still 2018 levels. The catch-up growth is inevitable. #undervalued #gem"},
    {"day": 16, "slot": 3, "topic": "AI",      "text": "AI voice agents are crossing the \"uncanny valley.\" They sound human. They pause. They laugh. Customer support is about to change forever. Are you ready? #voiceai #tech"},
    # DAY 17
    {"day": 17, "slot": 1, "topic": "LEADGEN", "text": "BOLD PREDICTION: Companies with sub-3% CAC will DESTROY competitors with 8%+ CAC by 2027. The divergence is NOW. GenAIx automation = sub-3% reality. #economics #cac"},
    {"day": 17, "slot": 2, "topic": "SPAIN",   "text": "Rental arbitrage play: Buy €300k property in Spain, rent at market rate (€1200/month = 4.8% yield). Year 10 = €144k profit + owned asset. Free money. #investing #cashflow"},
    {"day": 17, "slot": 3, "topic": "AI",      "text": "Prompt engineering is now a skill worth €100k+. Those who master ChatGPT prompts will build empires. Learning curve = 30 days. ROI = lifetime. #AI #skills"},
    # DAY 18
    {"day": 18, "slot": 1, "topic": "LEADGEN", "text": "Customer lifetime value increases 300% with automation (better experience = loyalty). Same customers, 3x profit. Automation = moat. Build it now. #automation #clv"},
    {"day": 18, "slot": 2, "topic": "SPAIN",   "text": "Spanish real estate cycle: Buy 2024-2025 (low), hold 2025-2027 (rise), sell 2027-2028 (peak). Total gain: 40-60%. That's your 5-year plan right there. #realestate #cycle"},
    {"day": 18, "slot": 3, "topic": "AI",      "text": "Your ChatGPT workflow: Daily standup recording → Auto-transcribed → Auto-summarized → Auto-sent to team. Takes 2 minutes. Team stays ALIGNED. Information flows INSTANTLY. #management #ops"},
    # DAY 19
    {"day": 19, "slot": 1, "topic": "LEADGEN", "text": "STAT: 73% of sales leaders say GenAI would double their output. Yet only 21% have implemented it. That's THE GAP. The winners are inside this 21%. Which side are you on? #stats #leadership"},
    {"day": 19, "slot": 2, "topic": "SPAIN",   "text": "Renovating in Spain: It WILL cost 20% more and take 2 months longer than you think. Factor that margin of safety in. If the deal still works, buy it. #construction #reality"},
    {"day": 19, "slot": 3, "topic": "AI",      "text": "Stop consuming content. Start generating it. AI lowers the barrier to creation. If you have expertise, you have no excuse not to share it at scale. #creator #economy"},
    # DAY 20
    {"day": 20, "slot": 1, "topic": "LEADGEN", "text": "The best sales rep in the world can handle 50 active conversations. A mediocre AI agent can handle 50,000. Quantity has a quality all its own. #scale #power"},
    {"day": 20, "slot": 2, "topic": "SPAIN",   "text": "Taxes in Spain are high? Myth. Wealth tax has high exemptions in many regions (Madrid, Andalucia). Do your research. Don't let tax fear kill your ROI. #taxes #facts"},
    {"day": 20, "slot": 3, "topic": "AI",      "text": "\"I don't have time to learn AI.\" You don't have time NOT to. It's like saying \"I don't have time to learn to read\" in 1500. It's the new literacy. #learning #necessity"},
    # DAY 21
    {"day": 21, "slot": 1, "topic": "LEADGEN", "text": "Inbound is great. Outbound is control. You can turn the dial up or down. Automated outbound gives you a \"Revenue Thermostat.\" Control your destiny. #revenue #control"},
    {"day": 21, "slot": 2, "topic": "SPAIN",   "text": "Student housing in Valencia: 2 universities, thousands of international students. Zero vacancy. Parents pay the rent (guaranteed). Recession-proof asset. #niche #investing"},
    {"day": 21, "slot": 3, "topic": "AI",      "text": "Analyze your calendar with AI. \"Where did I waste time last week?\" It categorizes meetings. Shows you the black holes. You reclaim 5 hours/week. #timemanagement #audit"},
    # DAY 22
    {"day": 22, "slot": 1, "topic": "LEADGEN", "text": "Email deliverability is the new SEO. If you're landing in spam, you don't exist. We use AI to warm up domains automatically. Technical excellence = Sales success. #deliverability #tech"},
    {"day": 22, "slot": 2, "topic": "SPAIN",   "text": "Costa del Sol: 300 days of sunshine, affordable property, expat community. Buy €250k, rent €1500/month. Tourism keeps income stable. Reliable passive stream. #realestate #lifestyle"},
    {"day": 22, "slot": 3, "topic": "AI",      "text": "Learning to prompt-engineer ChatGPT is like learning Excel in 2000. Game-changing skill. Those who skip it will be shocked by who's ahead in 2027. #AI #skills"},
    # DAY 23
    {"day": 23, "slot": 1, "topic": "LEADGEN", "text": "Customer service tickets: Average resolution time 4 hours. AI chatbot handles 70% in 5 minutes. Remaining 30% go to humans with full context. Same team, 10x efficiency. #automation #cs"},
    {"day": 23, "slot": 2, "topic": "SPAIN",   "text": "Buying land in Spain: High risk, high reward. Zoning laws change. If you navigate it right? 300% returns developing villas. If wrong? Zero. Know the game. #land #development"},
    {"day": 23, "slot": 3, "topic": "AI",      "text": "Translate your content into 10 languages instantly with AI. One post → Global audience. Why limit your ideas to one language? The world is open. #global #reach"},
    # DAY 24
    {"day": 24, "slot": 1, "topic": "LEADGEN", "text": "The \"Follow-Up\" is where money is made. Humans give up after 2 tries. Bots follow up 7 times over 3 months, politely, consistently. They catch the \"Yes\" that humans miss. #persistence #sales"},
    {"day": 24, "slot": 2, "topic": "SPAIN",   "text": "Bank repossessions in Spain: They still exist. 30-40% below market value. But you need cash and speed. We track these listings daily. #deals #bankowned"},
    {"day": 24, "slot": 3, "topic": "AI",      "text": "AI for negotiation: \"I received this offer. How should I counter to get +10%?\" It writes the script. Uses psychological principles. You send. You win. #negotiation #money"},
    # DAY 25
    {"day": 25, "slot": 1, "topic": "LEADGEN", "text": "Invoicing automated: Sent 5 minutes after client onboarding. 92% paid within 7 days vs 45% with manual reminder. Better cash flow = better business. Automate faster. #leadgen #cashflow"},
    {"day": 25, "slot": 2, "topic": "SPAIN",   "text": "Spain is the Florida of Europe. Retirees + Sun + Low Cost of Living. Demographics guarantee demand for the next 20 years. Bet on demographics. #macro #trends"},
    {"day": 25, "slot": 3, "topic": "AI",      "text": "ChatGPT as your accountability partner: \"Here's my goal + what I did today.\" It tracks. Reminds. Coaches. Motivates. 90 days of this = TRANSFORMATION. Discipline is AUTOMATED. #growth #habits"},
    # DAY 26
    {"day": 26, "slot": 1, "topic": "LEADGEN", "text": "Marketing attribution: Which ad brought the whale client? AI tracks the entire journey. You stop spending on what feels good and spend on what MAKES MONEY. #data #attribution"},
    {"day": 26, "slot": 2, "topic": "SPAIN",   "text": "Barcelona outskirts: Prices 50% of city center. Train to center 20 mins. Families moving out for space. That's the appreciation corridor. Buy the ripple effect. #strategy #location"},
    {"day": 26, "slot": 3, "topic": "AI",      "text": "Vector databases: The brain of your AI. It remembers everything your company has ever done. New employees query it. Instant onboarding. Institutional knowledge preserved. #tech #database"},
    # DAY 27
    {"day": 27, "slot": 1, "topic": "LEADGEN", "text": "Database queries: Humans 10 minutes, ChatGPT-SQL 10 seconds. Scale across company. Time saved compounds. At 100 employees doing this = 83 hours/day recovered. #automation #sql"},
    {"day": 27, "slot": 2, "topic": "SPAIN",   "text": "Tax benefits buying property in Spain: Mortgage interest deduction, rental depreciation, property tax breaks. Smart investors stack deductions. Wealth is tax-optimized wealth. #investing #taxes"},
    {"day": 27, "slot": 3, "topic": "AI",      "text": "Multimodal AI (text + image + video): Now you can train on everything simultaneously. Models understand context better. Next-gen tools launching monthly. #AI #future"},
    # DAY 28
    {"day": 28, "slot": 1, "topic": "LEADGEN", "text": "FINAL TRUTH: Every company will use GenAIx by 2027. The only question is: Are you first-mover advantage or late-stage scramble? Choose wisely. Time is UP. #urgency #adopt"},
    {"day": 28, "slot": 2, "topic": "SPAIN",   "text": "Community: The hidden value of Spanish property. Neighbors who look out for you. A culture of connection. You're buying into a social fabric, not just concrete. #community #life"},
    {"day": 28, "slot": 3, "topic": "AI",      "text": "AI won't make you creative if you're boring. It amplifies what you are. Be interesting. Be bold. Then use AI to be interesting and bold at scale. #truth #branding"},
    # DAY 29
    {"day": 29, "slot": 1, "topic": "LEADGEN", "text": "Quality assurance: Automated visual regression testing catches 99.5% of bugs. Manual QA = bottleneck. Automation = speed. Release cycles: 2 weeks → 2 days. Velocity. #automation #dev"},
    {"day": 29, "slot": 2, "topic": "SPAIN",   "text": "Final tip: Don't wait for \"perfect\" market conditions. They don't exist. Time in the market beats timing the market. Start your Spanish portfolio today. #action #investing"},
    {"day": 29, "slot": 3, "topic": "AI",      "text": "ChatGPT as your personal board of advisors: Run major decisions through it. Get roasted. Iterate. Make better choices. 30 days of this? Your decision-making quality DOUBLES. #decisions #strategy"},
    # DAY 30
    {"day": 30, "slot": 1, "topic": "LEADGEN", "text": "30 days from now, one of two things happens: Either you've IMPLEMENTED GenAIx lead automation, or you've DECIDED to stay uncompetitive. That's the only choice left. No middle ground. #final #choice"},
    {"day": 30, "slot": 2, "topic": "SPAIN",   "text": "30 days of Spanish Real Estate insights. Summary: High yields, strong growth, lifestyle bonus. The opportunity is open. Who is coming to Valencia with me? #summary #cta"},
    {"day": 30, "slot": 3, "topic": "AI",      "text": "30 days of AI insights. Summary: Automation is the lever. Speed is the currency. You have the tools. Now you need the will. Go build. #summary #execute"},
]

# Назначаем даты: день 6 = 2026-03-07, слоты: 08:00, 14:00, 20:00 Madrid
# До 29 марта: UTC+1. С 29 марта: UTC+2 (CEST)
slot_hours_madrid = {1: 8, 2: 14, 3: 20}

queue = []
for i, t in enumerate(tweets_raw):
    day_offset = t["day"] - 6  # день 6 = offset 0
    date = datetime(2026, 3, 7) + timedelta(days=day_offset)
    hour_madrid = slot_hours_madrid[t["slot"]]
    # UTC offset: до 29 марта = +1, с 29 марта = +2
    if date >= datetime(2026, 3, 29):
        utc_hour = hour_madrid - 2
    else:
        utc_hour = hour_madrid - 1
    
    scheduled_madrid = date.replace(hour=hour_madrid, minute=0, second=0)
    scheduled_utc = date.replace(hour=utc_hour, minute=0, second=0, tzinfo=timezone.utc)
    
    queue.append({
        "id": i + 1,
        "day": t["day"],
        "slot": t["slot"],
        "topic": t["topic"],
        "text": t["text"],
        "status": "scheduled",
        "scheduled_madrid": scheduled_madrid.strftime("%Y-%m-%dT%H:%M:%S"),
        "scheduled_utc": scheduled_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pending_since": None,
        "approved_text": None,
        "posted_at": None,
        "tweet_url": None
    })

with open("tweet_queue.json", "w", encoding="utf-8") as f:
    json.dump(queue, f, ensure_ascii=False, indent=2)

print(f"Generated {len(queue)} tweets")
print(f"First: Day {queue[0]['day']} | {queue[0]['scheduled_madrid']} | {queue[0]['topic']}")
print(f"Last:  Day {queue[-1]['day']} | {queue[-1]['scheduled_madrid']} | {queue[-1]['topic']}")
