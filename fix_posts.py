import re
with open('schedule_all_posts.cjs', 'r') as f:
    content = f.read()

# We want to replace the `const posts = [ ... ];` array.
# Let's find `const posts = [` and the corresponding `];` that closes it.
start_idx = content.find('const posts = [')
end_idx = content.find('];', start_idx) + 2

new_posts = """const posts = [
    {
      id: 1,
      type: 'regular',
      date: '06/25/2026',
      time: '8:00 AM',
      caption: `Here is what I learned building custom lead gen engines after scraping city planning commission minutes\\n\\nA month ago, a civil engineer PM got laid off and started building. Instead of jumping to standard automation tools, they coded custom scrapers in Python.\\n\\nThey realized city planning documents are a goldmine. The minutes list rezoning requests. Rezoning requests mean land development. Land development means new builders, attorneys, and contractors are about to get hired.\\n\\nBy writing a script that reads these minutes, extracts the affected businesses, and enriches the contact info, they built a highly targeted pipeline.\\n\\nThree lessons from this:\\n- Mine review data. Look at local trades businesses to spot cities with genuine labor shortages.\\n- Avoid building spam engines. Keep email lists short and clean. apollo exports are often dirty and increase bounce rates.\\n- Code your gateway. Using a Telegram gateway to manually review comment bot outputs keeps interactions authentic.\\n\\nDM me if you are trying to automate lead sourcing. I am building similar flows this week.\\n\\n#builderjourney #leadgeneration #automation`
    },
    {
      id: 2,
      type: 'regular',
      date: '06/25/2026',
      time: '12:00 PM',
      caption: `Vibe-coded automations are quietly breaking UAE business operations\\n\\nI keep talking to local founders who hired an "expert" to build n8n or Make scenarios. Three months later, the whole system stops working.\\n\\nHere are the 4 main reasons these setups fail in production:\\n- Happy path thinking. Most builders plan for things to go right. The minute there is a timeout or a missing field, the entire pipeline crashes.\\n- Zero error handling. There are no alerts when a run fails. The client only finds out when a customer complains.\\n- Lack of modularity. Huge scenarios that are impossible to edit. If you change one node, the whole system misfires.\\n- No documentation. No comments, no readme, no explanation of keys.\\n\\nWe need to stop treating business automation like a quick weekend hobby. If you are trusting your core operations to automated workflows, you need real software engineering principles.\\n\\n#automation #softwareengineering #dubaimarket`
    },
    {
      id: 3,
      type: 'carousel',
      date: '06/25/2026',
      time: '5:00 PM',
      caption: `Building automation tools that find hidden data. Here is the 5-step framework to extract leads from public city minutes.\\n\\n#buildinpublic #automation #softwareengineering`,
      assetPath: '/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/carousel-routine/output/2026-06-24/carousel-branded/linkedin-carousel-2026-06-24.pdf',
      title: 'AI City Minute Parser'
    },
    {
      id: 4,
      type: 'regular',
      date: '06/25/2026',
      time: '8:00 PM',
      caption: `The work that makes you money is rarely the work that makes you feel productive\\n\\nIt is easy to spend five hours optimizing your dashboard. Or tweaking CSS. Or reviewing new productivity software. At the end of the day, you feel like you did a lot.\\n\\nBut none of those hours brought in a single customer.\\n\\nThe most valuable work usually feels uncomfortable:\\n- Following up on warm leads\\n- Asking past clients for referrals\\n- Pitching regional businesses\\n- Doing direct outreach\\n\\nStop hiding behind easy setup tasks. Focus on the hard activities that grow the business.\\n\\n#productivity #entrepreneurship #solopreneur`
    }
  ];"""

new_content = content[:start_idx] + new_posts + content[end_idx:]

with open('schedule_all_posts.cjs', 'w') as f:
    f.write(new_content)
