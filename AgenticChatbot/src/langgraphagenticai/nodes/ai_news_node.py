from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate

class AINewsNode:
    def __init__(self,llm):
        """
        Initialize the AINewsNode with API keys for Tavily and GROQ
        """
        self.tavily=TavilyClient()
        self.llm=llm
        #this is used to capture various steps in this file so that later can be use for steps shown
        self.state={}

    def fetch_news(self,state:dict)->dict:
        """
        Fetch AI news based on the specified frequency.

        Args:
            state(dict): The state dictionary containing 'frequency'.

        Returns:
              dict: UPdated state with 'news_data' key containing fetched news.
        """

        frequency=state['messages'][0].content.lower()
        state['frequency']=frequency
        time_range_map={'daily':'d','weekly':'w','monthly':'m','year':'y'}
        days_map={'daily':1,'weekly':7,'monthly':30,'year':366}
        print("Frequency:", frequency)
        print("Calling Tavily...")
        response=self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and Globally",
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=20,
            days=days_map[frequency]
        )
        print("Results returned:", len(response.get("results", [])))
        state['news_data']=response.get('results',[])
        state['news_data']=state['news_data']
        return state
    
    def summarize_news(self,state:dict)->dict:
        """
        Summarize the fetched news using an LLm.

        Args:
           state(dict): The state dictionary containing 'news_data'.
        
        Returns:
            dict: UPdated state with 'summary' key containing the summarized news.    
        """
        news_items = state["news_data"]

        

        prompt_template=ChatPromptTemplate.from_messages([
            ("system","""Summarize AI news articles into markdown format. For each item include:
             -Date in *YYYY-MM-DD* format in IST timezone
             -Sort news by date wise (latest first)
             -Source URl as link
             Use format:
             ### [Date]
             -[Summary](URL)"""),
             ("user","Articles:\n{articles}")
        ])
        
        articles_str="\n\n".join([
            f"Content: {item.get('content','')}\nURL:{item.get('url','')}\n{item.get('published_date','')}"
            for item in news_items
        ])

        response=self.llm.invoke(prompt_template.format(articles=articles_str))
        print("LLM response:")
        print(response.content)
        state['summary']=response.content
        self.state['summary']=state['summary']
        if not news_items:
            print("No news returned from Tavily")
        return state
    
    def save_result(self,state):
        frequency=state['frequency']
        summary=state['summary']
        filename=f"./AINews/AINews{frequency}_summary.md"
        with open(filename,'w',encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
        state['filename']=filename
        return state