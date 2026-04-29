from __future__ import annotations

from datetime import date, timedelta

from hood_pipeline.domain.models import MonthlyRunResult


class MonthlyRunService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date) -> MonthlyRunResult:
        period_end = run_date.replace(day=1) - timedelta(days=1)
        period_start = period_end.replace(day=1)
        articles = [
            article
            for article in self.services.sqlite.relevant_articles_published_between(period_start, period_end)
            if self._is_reportable_article(article)
        ]
        mentions = self.services.sqlite.mentions_for_article_urls([article.url for article in articles])
        report_path = self.services.monthly_writer.write_monthly_report(
            run_date,
            period_start,
            period_end,
            articles,
            mentions,
        )
        return MonthlyRunResult(
            run_date=run_date,
            period_start=period_start,
            period_end=period_end,
            articles=articles,
            report_path=report_path,
        )

    def _is_reportable_article(self, article) -> bool:
        title = article.title.strip().lower()
        if title.startswith("skip to main site navigation"):
            return False
        if title.startswith("main navigation menu"):
            return False
        return True
