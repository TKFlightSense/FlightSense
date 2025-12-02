from services.statistics_service import StatisticsService
from models.enums.enums import Departments, LabelToDepartment
from datetime import datetime, timedelta

df = datetime(2025, 1, 1, 6, 0, 0)
dt = df + timedelta(hours=2)
statistics_service = StatisticsService()
print(statistics_service.get_label_sentiment_distribution(LabelToDepartment.checkin_process.name, df, dt))