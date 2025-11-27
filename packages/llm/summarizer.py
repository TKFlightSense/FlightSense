from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import date
from pathlib import Path
import json
import logging

import pandas as pd

from packages.llm.client import LLMClient
from packages.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)

#TODO: move them to the corresponding services later
#helpers
def get_aggregated_stats(self, department_name: str, date_from: str, date_to: str) -> pd.DataFrame:
        """
        Fetches aggregated statistics for a specific department within a date range.
        Groups by label, sentiment, and priority to prepare for multi-dimensional analysis.
        """
        query = """
            SELECT 
                label, 
                sentiment, 
                priority, 
                SUM(count) as count
            FROM statistics
            WHERE department = %s
              AND begin_date >= %s
              AND end_date <= %s
            GROUP BY label, sentiment, priority
        """
        
        try:
            df = pd.read_sql(
                query, 
                self.connection, 
                params=(department_name, date_from, date_to)
            )
            
            if df.empty:
                return pd.DataFrame(columns=['label', 'sentiment', 'priority', 'count'])
                
            return df

        except Exception as e:
            print(f"[Error] Failed to fetch aggregated stats: {e}")
            return pd.DataFrame(columns=['label', 'sentiment', 'priority', 'count'])
        
def get_department_comprehensive_stats( #refactor this
        self, 
        department_name: str, 
        date_from: str, 
        date_to: str
    ) -> Dict[str, Any]:
        """
        Calculates comprehensive multi-dimensional statistics for a department.
        Includes Label, Sentiment, and Priority distributions.
        """
        
        df = self.db.get_aggregated_stats(department_name, date_from, date_to)

        if df.empty:
            return {"error": "No data found", "meta": {"department": department_name}}

        total_reviews = df['count'].sum()
        
        def calculate_percentage(groupby_cols, normalize_col=None):
            """
            Gruplama yapar ve yüzdeye çevirir.
            Pandas kullanarak pivot table mantığı kurar.
            """
            if normalize_col:
                grouped = df.groupby(groupby_cols)['count'].sum()
                return (grouped / grouped.groupby(level=0).transform('sum') * 100).unstack(fill_value=0).to_dict(orient='index')
            else:
                return (df.groupby(groupby_cols)['count'].sum() / total_reviews * 100).to_dict()

        label_dist = calculate_percentage(['label'])
        
        sentiment_dist = calculate_percentage(['sentiment'])
        
        priority_dist = calculate_percentage(['priority'])

        label_sentiment_breakdown = calculate_percentage(['label', 'sentiment'], normalize_col=True)

        label_priority_breakdown = calculate_percentage(['label', 'priority'], normalize_col=True)

        sentiment_source_breakdown = calculate_percentage(['sentiment', 'label'], normalize_col=True)

        priority_source_breakdown = calculate_percentage(['priority', 'label'], normalize_col=True)

        return {
            "meta": {
                "department": department_name,
                "total_reviews": int(total_reviews),
                "date_range": {"from": date_from, "to": date_to}
            },
            "general_distribution": {
                "by_label": label_dist,
                "by_sentiment": sentiment_dist,
                "by_priority": priority_dist
            },
            "breakdowns": {
                "sentiment_within_labels": label_sentiment_breakdown,
                "priority_within_labels": label_priority_breakdown 
            },
            "sources": {
                "sources_of_sentiments": sentiment_source_breakdown,
                "sources_of_priorities": priority_source_breakdown
            }
        }

def get_global_aggregated_stats(self, date_from: str, date_to: str) -> pd.DataFrame:
        """
        Fetches aggregated statistics for the WHOLE company (all departments).
        """
        query = """
            SELECT 
                department, 
                sentiment, 
                priority, 
                SUM(count) as count
            FROM statistics
            WHERE begin_date >= %s AND end_date <= %s
            GROUP BY department, sentiment, priority
        """
        try:
            return pd.read_sql(query, self.connection, params=(date_from, date_to))
        except Exception as e:
            print(f"[Error] Failed to fetch global stats: {e}")
            return pd.DataFrame(columns=['department', 'sentiment', 'priority', 'count'])
        
def get_manager_general_stats(
        self, 
        date_from: str, 
        date_to: str
    ) -> Dict[str, Any]:
        """
        Calculates global statistics for Manager View.
        Answers:
        - Which department gets the most reviews?
        - What is the global sentiment/priority state?
        - Where do negative/high-priority reviews come from?
        """
        
        # 1. Global veriyi çek
        df = self.db.get_global_aggregated_stats(date_from, date_to)

        if df.empty:
            return {"error": "No data found", "meta": {"scope": "global"}}

        total_reviews = df['count'].sum()
        
        # --- Helper: Yüzde Hesaplayıcı ---
        def calculate_percentage(groupby_cols, normalize_col=None):
            if normalize_col:
                # Örn: Sentiment'e göre grupla, Departman dağılımını bul
                # (Negatiflerin %40'ı Sales, %60'ı Support gibi)
                grouped = df.groupby(groupby_cols)['count'].sum()
                return (grouped / grouped.groupby(level=0).transform('sum') * 100).unstack(fill_value=0).to_dict(orient='index')
            else:
                # Genel Pasta Grafikleri
                return (df.groupby(groupby_cols)['count'].sum() / total_reviews * 100).to_dict()

        # ==========================================
        # A. GENEL PASTA GRAFİKLERİ (Global Overview)
        # ==========================================
        
        # 1. Departman Dağılımı (Hangi departman ne kadar yoğun?)
        # Örn: {"Sales": 40.0, "HR": 10.0, "IT": 50.0}
        dept_dist = calculate_percentage(['department'])
        
        # 2. Global Sentiment Dağılımı
        # Örn: {"positive": 30.0, "negative": 70.0}
        global_sentiment_dist = calculate_percentage(['sentiment'])
        
        # 3. Global Priority Dağılımı
        # Örn: {"high": 20.0, "medium": 30.0, "low": 50.0}
        global_priority_dist = calculate_percentage(['priority'])

        # ==========================================
        # B. KAYNAK ANALİZİ (Source Analysis)
        # "Bu Negatifler/High Priority işler hangi departmandan geliyor?"
        # ==========================================
        
        # 4. Sentiment Kaynakları
        # Örn: Negative -> {"Sales": 20%, "TGS": 80%}
        sentiment_sources = calculate_percentage(['sentiment', 'department'], normalize_col=True)
        
        # 5. Priority Kaynakları
        # Örn: High Priority -> {"Kabin": 10%, "Bagaj": 90%}
        priority_sources = calculate_percentage(['priority', 'department'], normalize_col=True)

        return {
            "meta": {
                "scope": "Global Manager View",
                "total_reviews": int(total_reviews),
                "date_range": {"from": date_from, "to": date_to}
            },
            "global_distribution": {
                "by_department": dept_dist,      # Yük dağılımı
                "by_sentiment": global_sentiment_dist,
                "by_priority": global_priority_dist
            },
            "sources": {
                "sources_of_sentiments": sentiment_sources, # "Negatif yorumların sahibi kim?"
                "sources_of_priorities": priority_sources   # "Acil işlerin sahibi kim?"
            }
        }

# ==========================================
# 1. DEPARTMENT SPECIFIC REPORT PROMPT
# ==========================================

DEPARTMENT_REPORT_SYSTEM_PROMPT = """
You are an expert Data Analyst specializing in Customer Feedback and Operational Efficiency. 
Your job is to analyze the provided statistical JSON data for a specific department and write a comprehensive, actionable report.
Your tone should be professional, objective, and data-driven.
"""

DEPARTMENT_REPORT_USER_PROMPT = """
I will provide you with a JSON object containing statistical data for the department: **{department_name}**.
The data covers the period from **{date_from}** to **{date_to}**.

### The Data Structure explains:
1. **General Distribution**: Overall distribution of labels (topics), sentiments, and priority levels.
2. **Breakdowns**:
   - `sentiment_within_labels`: For a specific topic (e.g., 'food'), what is the sentiment?
   - `priority_within_labels`: For a specific topic, how urgent are the issues?
3. **Sources (Root Cause Analysis)**:
   - `sources_of_sentiments`: If sentiment is Negative, which label is the main culprit?
   - `sources_of_priorities`: If priority is High, which label is causing it?

### Your Task:
Write a "Department Performance Report" in Markdown format. The report must include:

1.  **Executive Summary**: A brief overview of the total volume and the general health (sentiment/priority) of the department.
2.  **Key Topics Analysis**: Which labels (topics) are the most discussed?
3.  **Risk Assessment (High Priority & Negative Areas)**:
    - Identify which topics have the highest percentage of **Negative** sentiment.
    - Identify which topics have the highest percentage of **High** priority.
    - Use the 'sources' data to pinpoint exactly where the bad metrics are coming from.
4.  **Operational Wins**: Highlight areas where sentiment is predominantly positive.
5.  **Recommendations**: Based on the data, suggest 2-3 focus areas for the department head.

### Constraints:
- Do not simply list numbers; interpret them (e.g., instead of "Food is 40%", say "Food is the primary driver of complaints, accounting for 40%...").
- Focus on significant values (e.g., >10%). Ignore negligible percentages.

### Data:
```json
{json_data}
"""

# ==========================================
# MANAGER (GLOBAL) REPORT PROMPTS
# ==========================================

MANAGER_REPORT_SYSTEM_PROMPT = """
You are a Senior Business Intelligence Consultant reporting to C-Level Executives.
Your goal is to provide a "Helicopter View" of the entire company's performance based on aggregated feedback data.
You must compare departments against each other, identify systemic bottlenecks, and provide high-level strategic advice.
Your tone should be professional, concise, and direct.
"""

MANAGER_REPORT_USER_PROMPT = """
I will provide you with a JSON object containing global statistical data for the entire company.
The data covers the period from **{date_from}** to **{date_to}**.

### The Data Structure explains:
1. **Global Distribution**: Overall company health (Sentiment, Priority) and Department workload distribution.
2. **Sources (Cross-Department Analysis)**:
   - `sources_of_sentiments`: Which department is contributing most to the Negative feedback?
   - `sources_of_priorities`: Which department is generating the most High Priority incidents?

### Your Task:
Write a "Executive Operational Report" in Markdown format. The report must include the following sections:

1.  **Global Health Check**:
    - Summarize the overall sentiment and priority scores for the company.
    - Is the general trend positive or worrying?

2.  **Departmental Workload & Performance**:
    - Which departments are handling the most volume?
    - Briefly mention which department is performing best (highest positive sentiment source).

3.  **Critical Bottlenecks (The "Red Zone")**:
    - **Who is driving Negativity?** Analyze `sources_of_sentiments` (specifically negative). Identify the department contributing most to negative customer experience.
    - **Who is driving Urgency?** Analyze `sources_of_priorities` (specifically high). Identify the department generating the most emergency tasks.
    *Use bold text to highlight these departments.*

4.  **Strategic Action Items**:
    - Provide 3 bullet points on where the management should focus their resources immediately to improve the metrics.

### Constraints:
- Be concise. Executives do not have time for fluff.
- Use **bold text** for key insights and department names.

### Data:
```json
{json_data}
"""

class StatsSummarizer:
  """
  High-level service for summarizing and generating report from airline passenger feedback.
  - Builds prompts ...
  - Calls LLM to generate a summary
  - Returns formatted string ...
  """

  def __init__(self, llm_client: Optional[LLMClient] = None, prompt_builder: Optional[PromptBuilder] = None):
    try:
      self.llm_client = llm_client or LLMClient()
    except Exception as e:
      logger.warning(f"Failed to initialize LLM client: {e}")
      self.llm_client = None
    self.prompt_builder = prompt_builder or PromptBuilder()

  def generate_department_report(self, department_name: str, date_from: str, date_to: str):
      if self.llm_client is None:
            logger.error("LLM client not initialized")
            return {"summary": []}
        
      stats_json = get_department_comprehensive_stats(department_name=department_name, date_from=date_from, date_to=date_to)
      data_str = json.dumps(stats_json, indent=2, ensure_ascii=False)
    
      formatted_prompt = DEPARTMENT_REPORT_USER_PROMPT.format(
          department_name=department_name,
          date_from=date_from,
          date_to=date_to,
          json_data=data_str
      )
      
      response = openai_client.chat.completions.create( #add llm client config
        model="gpt-4o", # or your preferred model
        messages=[
            {"role": "system", "content": DEPARTMENT_REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=0.3 # Keep it low for factual reporting
      )
    
      return response.choices[0].message.content.strip()
  
  def generate_manager_report(self, department_name: str, date_from: str, date_to: str):
      if self.llm_client is None:
            logger.error("LLM client not initialized")
            return {"summary": []}
        
      stats_json = get_manager_general_stats(date_from=date_from, date_to=date_to)
      data_str = json.dumps(stats_json, indent=2, ensure_ascii=False)
    
      formatted_prompt = MANAGER_REPORT_USER_PROMPT.format(
          date_from=date_from,
          date_to=date_to,
          json_data=data_str
      )
      
      response = openai_client.chat.completions.create( #add llm client config
        model="gpt-4o", # or your preferred model
        messages=[
            {"role": "system", "content": MANAGER_REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt}
        ],
        temperature=0.3 # Keep it low for factual reporting
      )
    
      return response.choices[0].message.content.strip()
      

# öne çıkan reviewlar (high priority) çekilsin dbden ve eklensin. db call sıkıntı böyle priority için ayrı column olmalı