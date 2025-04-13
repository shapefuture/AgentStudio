import pytest
from tools.web_scraper.scraper import WebScraperTool
from tools.analysis.openrouter import OpenRouterAnalysisTool
from tools.db.supabase_handler import SupabaseWriteTool
from praisonai import PraisonAI

class TestResearchAnalyst:
    @pytest.fixture
    def setup_tools(self):
        return {
            "scraper": WebScraperTool(),
            "analyzer": OpenRouterAnalysisTool(),
            "db": SupabaseWriteTool()
        }

    def test_web_scraper(self, setup_tools):
        scraper = setup_tools["scraper"]
        result = scraper.scrape("https://example.com", "h1")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_analysis_tool(self, setup_tools):
        analyzer = setup_tools["analyzer"]
        test_text = "Sample text for analysis"
        result = analyzer.analyze_text(test_text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_supabase_write(self, setup_tools):
        db = setup_tools["db"]
        test_data = {"title": "Test", "content": "Sample content"}
        result = db.write_data("test_table", test_data)
        assert result is not None

    def test_full_workflow(self):
        agents = PraisonAI(agents_config="docs/agents/research-analyst.mdx")
        result = agents.start({
            "urls": ["https://example.com"],
            "topic": "Sample research topic" 
        })
        assert "report_id" in result
        assert isinstance(result["report_id"], str)
