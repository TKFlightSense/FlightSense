import type { ManagerStatisticsData, Period } from "../services/api";

export const WEEKLY_MANAGER_STATS: ManagerStatisticsData = {
  period_label: "Last 7 days",
  total: 340,
  unique_reviews: 0,
  processed_segments: 0,

  // Sum of department-level counts:
  // positive: 147, negative: 150, neutral: 43
  sentiment_counts: {
    positive: 147,
    negative: 150,
    neutral: 43,
  },

  // Rough percentages matching above
  sentiment_percentages: {
    positive: 43, // 147 / 340 ≈ 43%
    negative: 44, // 150 / 340 ≈ 44%
    neutral: 13,  // 43 / 340 ≈ 13%
  },

  priority_counts: { high: 55, medium: 95, low: 190 },
  priority_percentages: { high: 16, medium: 28, low: 56 },

  department_distribution: {
    TGS: 65,
    IUIUB: 75,
    BMCOGM: 90,
    KHB: 20,
    RVBCM: 60,
    CMYM: 7,
    GYB: 23,
  },

  department_sentiment_distribution: {
    TGS: {
      sentiment: {
        counts: { positive: 28, negative: 30, neutral: 7 },
        percentage: { positive: 43, negative: 46, neutral: 11 },
      },
    },
    IUIUB: {
      sentiment: {
        counts: { positive: 33, negative: 28, neutral: 14 },
        percentage: { positive: 44, negative: 37, neutral: 19 },
      },
    },
    BMCOGM: {
      sentiment: {
        counts: { positive: 18, negative: 63, neutral: 9 },
        percentage: { positive: 20, negative: 70, neutral: 10 },
      },
    },
    KHB: {
      sentiment: {
        counts: { positive: 9, negative: 8, neutral: 3 },
        percentage: { positive: 45, negative: 40, neutral: 15 },
      },
    },
    RVBCM: {
      sentiment: {
        counts: { positive: 39, negative: 15, neutral: 6 },
        percentage: { positive: 65, negative: 25, neutral: 10 },
      },
    },
    CMYM: {
      sentiment: {
        counts: { positive: 5, negative: 1, neutral: 1 },
        percentage: { positive: 71, negative: 14, neutral: 14 },
      },
    },
    GYB: {
      sentiment: {
        counts: { positive: 15, negative: 5, neutral: 3 },
        percentage: { positive: 65, negative: 22, neutral: 13 },
      },
    },
  },

  historical_data: {
    day_1: { positive: 8, negative: 12, neutral: 3 },
    day_2: { positive: 12, negative: 15, neutral: 3 },
    day_3: { positive: 20, negative: 15, neutral: 5 },
    day_4: { positive: 18, negative: 20, neutral: 3 },
    day_5: { positive: 25, negative: 22, neutral: 4 },
    day_6: { positive: 28, negative: 22, neutral: 3 },
    day_7: { positive: 29, negative: 19, neutral: 4 },
  },

  high_priority_samples: {
    TGS: [
      "Queue for check-in was extremely long.",
      "Boarding order was not respected at the gate.",
      "No staff around to help with kiosk check-in.",
    ],
    IUIUB: [
      "Snack quality was lower than expected.",
      "Drinks were served only once on a 3-hour flight.",
      "Special meal request was not loaded.",
    ],
    BMCOGM: [
      "Baggage arrived visibly damaged.",
      "One of my bags was delayed to the next flight.",
      "Difficult to find the lost & found desk.",
    ],
    KHB: [
      "Cabin crew seemed stressed and impatient.",
      "Announcements were difficult to hear.",
      "Cabin temperature was uncomfortable.",
    ],
    RVBCM: [
      "Could not complete ticket change via the app.",
      "Fees for date change were not clear.",
      "Refund process took longer than expected.",
    ],
    CMYM: [
      "Call center disconnected in the middle of the call.",
      "IVR menu was confusing to navigate.",
      "Agent did not call back as promised.",
    ],
    GYB: [
      "Promo fare conditions were not obvious on the website.",
      "Miles were not credited automatically after the flight.",
      "Dynamic pricing felt unfair for last-minute booking.",
    ],
  },
};

export const MONTHLY_MANAGER_STATS: ManagerStatisticsData = {
  period_label: "Last 30 days",
  total: 1460,
  unique_reviews: 0,
  processed_segments: 0,

  // Sum of department-level counts:
  // positive: 900, negative: 452, neutral: 108
  sentiment_counts: {
    positive: 900,
    negative: 452,
    neutral: 108,
  },

  sentiment_percentages: {
    positive: 62, // ≈61.6%
    negative: 31, // ≈31.0%
    neutral: 7,   // ≈7.4%
  },

  priority_counts: { high: 220, medium: 600, low: 640 },
  priority_percentages: { high: 15, medium: 41, low: 44 },

  department_distribution: {
    TGS: 420,
    IUIUB: 310,
    BMCOGM: 280,
    KHB: 230,
    RVBCM: 90,
    CMYM: 70,
    GYB: 60,
  },

  department_sentiment_distribution: {
    TGS: {
      sentiment: {
        counts: { positive: 255, negative: 135, neutral: 30 },
        percentage: { positive: 61, negative: 32, neutral: 7 },
      },
    },
    IUIUB: {
      sentiment: {
        counts: { positive: 195, negative: 95, neutral: 20 },
        percentage: { positive: 63, negative: 31, neutral: 6 },
      },
    },
    BMCOGM: {
      sentiment: {
        counts: { positive: 175, negative: 85, neutral: 20 },
        percentage: { positive: 62, negative: 30, neutral: 8 },
      },
    },
    KHB: {
      sentiment: {
        counts: { positive: 145, negative: 70, neutral: 15 },
        percentage: { positive: 63, negative: 30, neutral: 7 },
      },
    },
    RVBCM: {
      sentiment: {
        counts: { positive: 53, negative: 28, neutral: 9 },
        percentage: { positive: 59, negative: 31, neutral: 10 },
      },
    },
    CMYM: {
      sentiment: {
        counts: { positive: 41, negative: 21, neutral: 8 },
        percentage: { positive: 59, negative: 30, neutral: 11 },
      },
    },
    GYB: {
      sentiment: {
        counts: { positive: 36, negative: 18, neutral: 6 },
        percentage: { positive: 60, negative: 30, neutral: 10 },
      },
    },
  },

  historical_data: {
    week_1: { positive: 165, negative: 60, neutral: 15 },
    week_2: { positive: 190, negative: 85, neutral: 15 },
    week_3: { positive: 180, negative: 105, neutral: 15 },
    week_4: { positive: 365, negative: 230, neutral: 35 },
  },

  high_priority_samples: {
    TGS: [
      "Check-in line took over 40 minutes.",
      "Boarding announcements were confusing at the gate.",
      "Ground staff did not guide transfer passengers clearly.",
    ],
    IUIUB: [
      "Meal was served cold on a long-haul flight.",
      "Very limited vegetarian options available.",
      "Beverage service started very late into the flight.",
    ],
    BMCOGM: [
      "My baggage was missing after a transfer in Istanbul.",
      "Waited almost 2 hours at baggage claim.",
      "No proactive information was given about delayed bags.",
    ],
    KHB: [
      "Cabin crew response time to call button was very slow.",
      "Seat comfort was poor for an overnight flight.",
      "Lavatories were not cleaned frequently enough.",
    ],
    RVBCM: [
      "My booking was changed without clear explanation.",
      "Had trouble modifying the ticket online.",
      "Fare rules were not clearly explained during purchase.",
    ],
    CMYM: [
      "Long waiting time to reach the call center.",
      "Agent could not resolve my issue in a single call.",
      "Information from different agents was inconsistent.",
    ],
    GYB: [
      "Ticket prices changed drastically within a few hours.",
      "Miles earning rules felt unclear for this flight.",
      "Promo fare conditions were confusing at checkout.",
    ],
  },
};

export const YEARLY_MANAGER_STATS: ManagerStatisticsData = {
  period_label: "Last 12 months",
  total: 16900,
  unique_reviews: 0,
  processed_segments: 0,

  // Sum of department-level counts:
  // positive: 12670, negative: 3040, neutral: 1190
  sentiment_counts: {
    positive: 12670,
    negative: 3040,
    neutral: 1190,
  },

  sentiment_percentages: {
    positive: 75, // ≈75.0%
    negative: 18, // ≈18.0%
    neutral: 7,   // ≈7.0%
  },

  priority_counts: { high: 3887, medium: 4563, low: 8450 },
  priority_percentages: { high: 23, medium: 27, low: 50 },

  department_distribution: {
    TGS: 3700,
    IUIUB: 3100,
    BMCOGM: 2700,
    KHB: 2450,
    RVBCM: 2200,
    CMYM: 1900,
    GYB: 850,
  },

  department_sentiment_distribution: {
    TGS: {
      sentiment: {
        counts: { positive: 2780, negative: 700, neutral: 220 },
        percentage: { positive: 75, negative: 19, neutral: 6 },
      },
    },
    IUIUB: {
      sentiment: {
        counts: { positive: 2400, negative: 540, neutral: 160 },
        percentage: { positive: 77, negative: 17, neutral: 6 },
      },
    },
    BMCOGM: {
      sentiment: {
        counts: { positive: 2050, negative: 480, neutral: 170 },
        percentage: { positive: 76, negative: 18, neutral: 6 },
      },
    },
    KHB: {
      sentiment: {
        counts: { positive: 1820, negative: 430, neutral: 200 },
        percentage: { positive: 74, negative: 18, neutral: 8 },
      },
    },
    RVBCM: {
      sentiment: {
        counts: { positive: 1680, negative: 350, neutral: 170 },
        percentage: { positive: 76, negative: 16, neutral: 8 },
      },
    },
    CMYM: {
      sentiment: {
        counts: { positive: 1430, negative: 300, neutral: 170 },
        percentage: { positive: 75, negative: 16, neutral: 9 },
      },
    },
    GYB: {
      sentiment: {
        counts: { positive: 510, negative: 240, neutral: 100 },
        percentage: { positive: 60, negative: 28, neutral: 12 },
      },
    },
  },

  historical_data: {
    month_1: { positive: 790, negative: 170, neutral: 40 },
    month_2: { positive: 1200, negative: 250, neutral: 40 },
    month_3: { positive: 980, negative: 135, neutral: 35 },
    month_4: { positive: 1800, negative: 360, neutral: 70 },
    month_5: { positive: 720, negative: 240, neutral: 40 },
    month_6: { positive: 2020, negative: 160, neutral: 60 },
    month_7: { positive: 880, negative: 290, neutral: 50 },
    month_8: { positive: 1650, negative: 210, neutral: 50 },
    month_9: { positive: 590, negative: 260, neutral: 40 },
    month_10: { positive: 1500, negative: 170, neutral: 30 },
    month_11: { positive: 730, negative: 150, neutral: 40 },
    month_12: { positive: 1040, negative: 600, neutral: 70 },
  },

  high_priority_samples: {
    TGS: [
      "Seasonal peaks created very long queues at check-in.",
      "Summer flights had repeated boarding delays.",
      "Transfer guidance was confusing during peak months.",
    ],
    IUIUB: [
      "Quality of hot meals varied significantly between routes.",
      "Popular drink options frequently out of stock.",
      "Snack service downgraded on some flights.",
    ],
    BMCOGM: [
      "Frequent reports of delayed luggage on connecting flights.",
      "Baggage damage complaints increased in summer.",
      "Passengers struggled to get timely status updates.",
    ],
    KHB: [
      "Cabin announcements sometimes unclear on international routes.",
      "Night flights received fewer cabin rounds than expected.",
      "Cleaning standards fluctuated between aircraft types.",
    ],
    RVBCM: [
      "Booking change rules varied between channels.",
      "Refund processing time was longer in peak season.",
      "Promo tickets had stricter change conditions than expected.",
    ],
    CMYM: [
      "High call volumes in holiday seasons led to long waits.",
      "Some agents gave inconsistent information about disruptions.",
      "Callbacks were sometimes delayed or missed.",
    ],
    GYB: [
      "Dynamic pricing during peak periods frustrated frequent flyers.",
      "Award seat availability was limited on popular routes.",
      "Loyalty benefits were perceived as weaker after fare changes.",
    ],
  },
};

export const MOCK_MANAGER_STATS_BY_RANGE: Record<Period, ManagerStatisticsData> =
  {
    weekly: WEEKLY_MANAGER_STATS,
    monthly: MONTHLY_MANAGER_STATS,
    yearly: YEARLY_MANAGER_STATS,
  };
