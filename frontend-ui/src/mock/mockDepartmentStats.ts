import type { DepartmentStatisticsData, Period } from "../services/api";
import { DEPARTMENT_CODE_TO_LABEL, type DepartmentId,  } from "../departmentConfig";

type DepartmentStatsByPeriod = Record<Period, DepartmentStatisticsData>;


export const MOCK_DEPARTMENT_STATS_BY_RANGE: Record<
  DepartmentId,
  DepartmentStatsByPeriod
> = {
  /* ===================== IUIUB ===================== */
  IUIUB: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["IUIUB"],
      total: 75,

      sentiment_counts: {
        positive: 45,
        negative: 30,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: Math.round((45 / 75) * 100),
        negative: Math.round((30 / 75) * 100),
        neutral: 0,
      },

      priority_counts: {
        high: Math.round(75 * 0.2),
        medium: Math.round(75 * 0.35),
        low: 75 - Math.round(75 * 0.2) - Math.round(75 * 0.35),
      },
      priority_percentages: {
        high: Math.round(
          (Math.round(75 * 0.2) / 75) * 100
        ),
        medium: Math.round(
          (Math.round(75 * 0.35) / 75) * 100
        ),
        low: Math.round(
          ((75 -
            Math.round(75 * 0.2) -
            Math.round(75 * 0.35)) /
            75) *
            100
        ),
      },



      label_distribution: {
        inflight_experience_food_beverage: {
          counts: { positive: 29, negative: 19, neutral: 0 },
          percentage: {
            positive: Math.round((29 / 48) * 100),
            negative: Math.round((19 / 48) * 100),
            neutral: 0,
          },
        },
        inflight_experience_entertainment: {
          counts: { positive: 16, negative: 11, neutral: 0 },
          percentage: {
            positive: Math.round((16 / 27) * 100),
            negative: Math.round((11 / 27) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 7, negative: 4, neutral: 0 },
        day_2: { positive: 7, negative: 4, neutral: 0 },
        day_3: { positive: 6, negative: 4, neutral: 0 },
        day_4: { positive: 7, negative: 5, neutral: 0 },
        day_5: { positive: 6, negative: 4, neutral: 0 },
        day_6: { positive: 6, negative: 4, neutral: 0 },
        day_7: { positive: 6, negative: 5, neutral: 0 },
      },

      high_priority_samples: {
        inflight_experience_food_beverage: [
          "Meal was served cold on a 4-hour flight.",
          "Portions felt small compared to flight duration.",
          "Very limited vegetarian / special meal options.",
        ],
        inflight_experience_entertainment: [
          "Seatback screen froze repeatedly.",
          "Movie selection was limited for this route.",
          "Headphones had poor audio and needed replacement.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["IUIUB"],
      total: 310,

      sentiment_counts: {
        positive: 207,
        negative: 103,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: 67,
        negative: 33,
        neutral: 0,
      },

      priority_counts: {
        high: 50,
        medium: 140,
        low: 120,
      },
      priority_percentages: {
        high: 16,
        medium: 45,
        low: 39,
      },

    

      label_distribution: {
        inflight_experience_food_beverage: {
          counts: { positive: 130, negative: 70, neutral: 0 },
          percentage: {
            positive: Math.round((130 / 200) * 100),
            negative: Math.round((70 / 200) * 100),
            neutral: 0,
          },
        },
        inflight_experience_entertainment: {
          counts: { positive: 77, negative: 33, neutral: 0 },
          percentage: {
            positive: Math.round((77 / 110) * 100),
            negative: Math.round((33 / 110) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 60, negative: 25, neutral: 0 },
        week_2: { positive: 55, negative: 18, neutral: 0 },
        week_3: { positive: 65, negative: 20, neutral: 0 },
        week_4: { positive: 50, negative: 17, neutral: 0 },
      },

      high_priority_samples: {
        inflight_experience_food_beverage: [
          "Meal was served cold on a long-haul flight.",
          "Portions felt small compared to flight duration.",
          "Very limited vegetarian / special meal options.",
        ],
        inflight_experience_entertainment: [
          "Seatback screen was not working during most of the flight.",
          "Movie selection was limited for a long-haul route.",
          "Headphones had poor audio quality and needed replacement.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["IUIUB"],
      total: 3100,

      sentiment_counts: {
        positive: 2500,
        negative: 600,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: Math.round((2500 / 3100) * 100),
        negative: Math.round((600 / 3100) * 100),
        neutral: 0,
      },

      priority_counts: {
        high: Math.round(3100 * 0.23),
        medium: Math.round(3100 * 0.27),
        low:
          3100 -
          Math.round(3100 * 0.23) -
          Math.round(3100 * 0.27),
      },
      priority_percentages: {
        high: Math.round(
          (Math.round(3100 * 0.23) / 3100) * 100
        ),
        medium: Math.round(
          (Math.round(3100 * 0.27) / 3100) * 100
        ),
        low: Math.round(
          ((3100 -
            Math.round(3100 * 0.23) -
            Math.round(3100 * 0.27)) /
            3100) *
            100
        ),
      },


      label_distribution: {
        inflight_experience_food_beverage: {
          counts: { positive: 1650, negative: 350, neutral: 0 },
          percentage: {
            positive: Math.round((1650 / 2000) * 100),
            negative: Math.round((350 / 2000) * 100),
            neutral: 0,
          },
        },
        inflight_experience_entertainment: {
          counts: { positive: 850, negative: 250, neutral: 0 },
          percentage: {
            positive: Math.round((850 / 1100) * 100),
            negative: Math.round((250 / 1100) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 180, negative: 40, neutral: 0 },
        month_2: { positive: 200, negative: 45, neutral: 0 },
        month_3: { positive: 210, negative: 50, neutral: 0 },
        month_4: { positive: 220, negative: 55, neutral: 0 },
        month_5: { positive: 215, negative: 50, neutral: 0 },
        month_6: { positive: 230, negative: 55, neutral: 0 },
        month_7: { positive: 240, negative: 60, neutral: 0 },
        month_8: { positive: 235, negative: 55, neutral: 0 },
        month_9: { positive: 210, negative: 50, neutral: 0 },
        month_10: { positive: 210, negative: 50, neutral: 0 },
        month_11: { positive: 205, negative: 45, neutral: 0 },
        month_12: { positive: 245, negative: 45, neutral: 0 },
      },

      high_priority_samples: {
          inflight_experience_food_beverage: [
            "Meal was served cold on a long-haul flight.",
            "Portions felt small compared to flight duration.",
            "Very limited vegetarian / special meal options.",
          ],
          inflight_experience_entertainment: [
            "Seatback screen was not working during most of the flight.",
            "Movie selection was limited for a long-haul route.",
            "Headphones had poor audio quality and needed replacement.",
          ],
        },

    },
  },

  /* ===================== BMCOGM ===================== */
  BMCOGM: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["BMCOGM"],
      total: 90,

      sentiment_counts: {
        positive: 20,
        negative: 70,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: Math.round((20 / 90) * 100),
        negative: Math.round((70 / 90) * 100),
        neutral: 0,
      },

      priority_counts: {
        high: Math.round(90 * 0.2),
        medium: Math.round(90 * 0.35),
        low: 90 - Math.round(90 * 0.2) - Math.round(90 * 0.35),
      },
      priority_percentages: {
        high: Math.round(
          (Math.round(90 * 0.2) / 90) * 100
        ),
        medium: Math.round(
          (Math.round(90 * 0.35) / 90) * 100
        ),
        low: Math.round(
          ((90 -
            Math.round(90 * 0.2) -
            Math.round(90 * 0.35)) /
            90) *
            100
        ),
      },

      label_distribution: {
        baggage_lost: {
          counts: { positive: 12, negative: 49, neutral: 0 },
          percentage: {
            positive: Math.round((12 / 61) * 100),
            negative: Math.round((49 / 61) * 100),
            neutral: 0,
          },
        },
        baggage_damaged: {
          counts: { positive: 8, negative: 21, neutral: 0 },
          percentage: {
            positive: Math.round((8 / 29) * 100),
            negative: Math.round((21 / 29) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 4, negative: 7, neutral: 0 },
        day_2: { positive: 3, negative: 10, neutral: 0 },
        day_3: { positive: 3, negative: 10, neutral: 0 },
        day_4: { positive: 4, negative: 11, neutral: 0 },
        day_5: { positive: 2, negative: 10, neutral: 0 },
        day_6: { positive: 2, negative: 11, neutral: 0 },
        day_7: { positive: 2, negative: 11, neutral: 0 },
      },

      high_priority_samples: {
        baggage_lost: [
          "Bag did not arrive on the carousel.",
          "Had to file a lost-baggage report with no clear ETA.",
          "Missed my transfer while resolving lost baggage.",
        ],
        baggage_damaged: [
          "Suitcase arrived with a broken wheel.",
          "Handle was torn off during handling.",
          "Hard-shell case was visibly cracked on arrival.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["BMCOGM"],
      total: 280,

      sentiment_counts: {
        positive: 187,
        negative: 93,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: 67,
        negative: 33,
        neutral: 0,
      },

      priority_counts: {
        high: 40,
        medium: 120,
        low: 120,
      },
      priority_percentages: {
        high: 14,
        medium: 43,
        low: 43,
      },


      label_distribution: {
        baggage_lost: {
          counts: { positive: 120, negative: 70, neutral: 0 },
          percentage: {
            positive: Math.round((120 / 190) * 100),
            negative: Math.round((70 / 190) * 100),
            neutral: 0,
          },
        },
        baggage_damaged: {
          counts: { positive: 67, negative: 23, neutral: 0 },
          percentage: {
            positive: Math.round((67 / 90) * 100),
            negative: Math.round((23 / 90) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 40, negative: 25, neutral: 0 },
        week_2: { positive: 55, negative: 38, neutral: 0 },
        week_3: { positive: 65, negative: 20, neutral: 0 },
        week_4: { positive: 20, negative: 10, neutral: 0 },
      },

      high_priority_samples: {
        baggage_lost: [
          "My baggage did not arrive on the carousel after landing.",
          "I missed my connection while trying to resolve a lost bag issue.",
          "I received no clear information about when my bag would be delivered.",
        ],
        baggage_damaged: [
          "The suitcase arrived with a broken wheel and cracked shell.",
          "Handle was torn off and the bag could not be rolled anymore.",
          "Contents were damaged due to the bag arriving open.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["BMCOGM"],
      total: 2700,

      sentiment_counts: {
        positive: 2200,
        negative: 500,
        neutral: 0,
      },
      sentiment_percentages: {
        positive: Math.round((2200 / 2700) * 100),
        negative: Math.round((500 / 2700) * 100),
        neutral: 0,
      },

      priority_counts: {
        high: Math.round(2700 * 0.23),
        medium: Math.round(2700 * 0.27),
        low:
          2700 -
          Math.round(2700 * 0.23) -
          Math.round(2700 * 0.27),
      },
      priority_percentages: {
        high: Math.round(
          (Math.round(2700 * 0.23) / 2700) * 100
        ),
        medium: Math.round(
          (Math.round(2700 * 0.27) / 2700) * 100
        ),
        low: Math.round(
          ((2700 -
            Math.round(2700 * 0.23) -
            Math.round(2700 * 0.27)) /
            2700) *
            100
        ),
      },


      label_distribution: {
        baggage_lost: {
          counts: { positive: 1490, negative: 342, neutral: 0 },
          percentage: {
            positive: Math.round((1490 / 1832) * 100),
            negative: Math.round((342 / 1832) * 100),
            neutral: 0,
          },
        },
        baggage_damaged: {
          counts: { positive: 710, negative: 158, neutral: 0 },
          percentage: {
            positive: Math.round((710 / 868) * 100),
            negative: Math.round((158 / 868) * 100),
            neutral: 0,
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 180, negative: 40, neutral: 0 },
        month_2: { positive: 190, negative: 45, neutral: 0 },
        month_3: { positive: 195, negative: 50, neutral: 0 },
        month_4: { positive: 205, negative: 55, neutral: 0 },
        month_5: { positive: 200, negative: 45, neutral: 0 },
        month_6: { positive: 210, negative: 50, neutral: 0 },
        month_7: { positive: 220, negative: 55, neutral: 0 },
        month_8: { positive: 215, negative: 45, neutral: 0 },
        month_9: { positive: 200, negative: 45, neutral: 0 },
        month_10: { positive: 195, negative: 45, neutral: 0 },
        month_11: { positive: 195, negative: 40, neutral: 0 },
        month_12: { positive: 195, negative: 35, neutral: 0 },
      },

      high_priority_samples: {
        baggage_lost: [
          "My baggage did not arrive on the carousel after landing.",
          "I missed my connection while trying to resolve a lost bag issue.",
          "I received no clear information about when my bag would be delivered.",
        ],
        baggage_damaged: [
          "The suitcase arrived with a broken wheel and cracked shell.",
          "Handle was torn off and the bag could not be rolled anymore.",
          "Contents were damaged due to the bag arriving open.",
        ],
      },

    },
  },
  /* ===================== KHB ===================== */
  KHB: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["KHB"],
      total: 20,

      sentiment_counts: {
        positive: 9,
        negative: 9,
        neutral: 2,
      },
      sentiment_percentages: {
        positive: Math.round((9 / 20) * 100),   // 45
        negative: Math.round((9 / 20) * 100),  // 45
        neutral: Math.round((2 / 20) * 100),   // 10
      },

      priority_counts: {
        high: Math.round(20 * 0.2),      // 4
        medium: Math.round(20 * 0.35),   // 7
        low: 20 - Math.round(20 * 0.2) - Math.round(20 * 0.35), // 9
      },
      priority_percentages: {
        high: Math.round((Math.round(20 * 0.2) / 20) * 100),
        medium: Math.round((Math.round(20 * 0.35) / 20) * 100),
        low: Math.round(
          ((20 -
            Math.round(20 * 0.2) -
            Math.round(20 * 0.35)) /
            20) *
            100
        ),
      },

      label_distribution: {
        inflight_experience_seats_comfort: {
          counts: { positive: 4, negative: 3, neutral: 1 },
          percentage: {
            positive: Math.round((4 / 8) * 100),
            negative: Math.round((3 / 8) * 100),
            neutral: Math.round((1 / 8) * 100),
          },
        },
        inflight_experience_cabin_service: {
          counts: { positive: 3, negative: 3, neutral: 1 },
          percentage: {
            positive: Math.round((3 / 7) * 100),
            negative: Math.round((3 / 7) * 100),
            neutral: Math.round((1 / 7) * 100),
          },
        },
        inflight_experience_cleanliness: {
          counts: { positive: 2, negative: 2, neutral: 1 },
          percentage: {
            positive: Math.round((2 / 5) * 100),
            negative: Math.round((2 / 5) * 100),
            neutral: Math.round((1 / 5) * 100),
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 2, negative: 1, neutral: 0 },
        day_2: { positive: 2, negative: 1, neutral: 0 },
        day_3: { positive: 1, negative: 1, neutral: 1 },
        day_4: { positive: 2, negative: 2, neutral: 0 },
        day_5: { positive: 1, negative: 2, neutral: 0 },
        day_6: { positive: 1, negative: 1, neutral: 1 },
        day_7: { positive: 0, negative: 1, neutral: 0 },
      },

      high_priority_samples: {
        inflight_experience_seats_comfort: [
          "Seat cushion felt worn and hard.",
          "Legroom was not enough to sit comfortably.",
          "Seat recline function was not working properly.",
        ],
        inflight_experience_cabin_service: [
          "Crew seemed rushed and less attentive.",
          "Drink service was skipped for some rows.",
          "Call button response took a long time.",
        ],
        inflight_experience_cleanliness: [
          "Tray table had visible stains.",
          "Lavatory floor was wet and not cleaned.",
          "Seat pocket contained trash from previous flight.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["KHB"],
      total: 230,

      sentiment_counts: {
        positive: 150,
        negative: 68,
        neutral: 12,
      },
      sentiment_percentages: {
        positive: Math.round((150 / 230) * 100),
        negative: Math.round((68 / 230) * 100),
        neutral: Math.round((12 / 230) * 100),
      },

      priority_counts: {
        high: 15,
        medium: 90,
        low: 125,
      },
      priority_percentages: {
        high: Math.round((15 / 230) * 100),
        medium: Math.round((90 / 230) * 100),
        low: Math.round((125 / 230) * 100),
      },

      label_distribution: {
        inflight_experience_seats_comfort: {
          counts: { positive: 55, negative: 30, neutral: 5 },
          percentage: {
            positive: Math.round((55 / 90) * 100),
            negative: Math.round((30 / 90) * 100),
            neutral: Math.round((5 / 90) * 100),
          },
        },
        inflight_experience_cabin_service: {
          counts: { positive: 55, negative: 22, neutral: 3 },
          percentage: {
            positive: Math.round((55 / 80) * 100),
            negative: Math.round((22 / 80) * 100),
            neutral: Math.round((3 / 80) * 100),
          },
        },
        inflight_experience_cleanliness: {
          counts: { positive: 40, negative: 16, neutral: 4 },
          percentage: {
            positive: Math.round((40 / 60) * 100),
            negative: Math.round((16 / 60) * 100),
            neutral: Math.round((4 / 60) * 100),
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 30, negative: 15, neutral: 2 },
        week_2: { positive: 25, negative: 16, neutral: 3 },
        week_3: { positive: 35, negative: 20, neutral: 3 },
        week_4: { positive: 60, negative: 17, neutral: 4 },
      },

      high_priority_samples: {
        inflight_experience_seats_comfort: [
          "Seat cushion felt very worn and uncomfortable.",
          "Legroom was not sufficient for a long-haul overnight flight.",
          "Seat recline was limited and made it hard to rest.",
        ],
        inflight_experience_cabin_service: [
          "Call button response time was very slow.",
          "Crew seemed overwhelmed and not very attentive.",
          "Service sequence felt unorganized and confusing.",
        ],
        inflight_experience_cleanliness: [
          "Tray table and armrest were visibly dirty during boarding.",
          "Lavatory was not cleaned frequently during the flight.",
          "Seat pocket contained rubbish from the previous passenger.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["KHB"],
      total: 2450,

      sentiment_counts: {
        positive: 1940,
        negative: 390,
        neutral: 120,
      },
      sentiment_percentages: {
        positive: Math.round((1940 / 2450) * 100),
        negative: Math.round((390 / 2450) * 100),
        neutral: Math.round((120 / 2450) * 100),
      },

      priority_counts: {
        high: Math.round(2450 * 0.23),
        medium: Math.round(2450 * 0.27),
        low:
          2450 -
          Math.round(2450 * 0.23) -
          Math.round(2450 * 0.27),
      },
      priority_percentages: {
        high: Math.round((Math.round(2450 * 0.23) / 2450) * 100),
        medium: Math.round((Math.round(2450 * 0.27) / 2450) * 100),
        low: Math.round(
          ((2450 -
            Math.round(2450 * 0.23) -
            Math.round(2450 * 0.27)) /
            2450) *
            100
        ),
      },


      label_distribution: {
        inflight_experience_seats_comfort: {
          counts: { positive: 780, negative: 150, neutral: 29 },
          percentage: {
            positive: Math.round((780 / 959) * 100),
            negative: Math.round((150 / 959) * 100),
            neutral: Math.round((29 / 959) * 100),
          },
        },
        inflight_experience_cabin_service: {
          counts: { positive: 700, negative: 120, neutral: 32 },
          percentage: {
            positive: Math.round((700 / 852) * 100),
            negative: Math.round((120 / 852) * 100),
            neutral: Math.round((32 / 852) * 100),
          },
        },
        inflight_experience_cleanliness: {
          counts: { positive: 460, negative: 120, neutral: 59 },
          percentage: {
            positive: Math.round((460 / 639) * 100),
            negative: Math.round((120 / 639) * 100),
            neutral: Math.round((59 / 639) * 100),
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 160, negative: 40, neutral: 5 },
        month_2: { positive: 165, negative: 40, neutral: 5 },
        month_3: { positive: 170, negative: 45, neutral: 5 },
        month_4: { positive: 175, negative: 45, neutral: 5 },
        month_5: { positive: 170, negative: 40, neutral: 5 },
        month_6: { positive: 175, negative: 45, neutral: 5 },
        month_7: { positive: 180, negative: 45, neutral: 5 },
        month_8: { positive: 175, negative: 40, neutral: 5 },
        month_9: { positive: 165, negative: 40, neutral: 5 },
        month_10: { positive: 165, negative: 40, neutral: 5 },
        month_11: { positive: 160, negative: 35, neutral: 5 },
        month_12: { positive: 170, negative: 35, neutral: 5 },
      },

      high_priority_samples: {
        inflight_experience_seats_comfort: [
          "Seat comfort remained a recurring concern on long-haul routes.",
          "Some older aircraft had noticeably less comfortable seats.",
          "Extra-legroom seats did not always feel significantly better.",
        ],
        inflight_experience_cabin_service: [
          "Consistency of service differed noticeably between routes.",
          "Night flights sometimes had fewer visible cabin rounds.",
          "Service flow felt rushed on heavily booked flights.",
        ],
        inflight_experience_cleanliness: [
          "Cleaning quality varied between aircraft types.",
          "Lavatory cleanliness was sometimes below expectations on long flights.",
          "Seat area was not always reset properly between connections.",
        ],
      },
    },
  },
  /* ===================== TGS ===================== */
  TGS: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["TGS"],
      total: 65,

      sentiment_counts: {
        positive: 30,
        negative: 30,
        neutral: 5,
      },
      sentiment_percentages: {
        positive: Math.round((30 / 65) * 100),
        negative: Math.round((30 / 65) * 100),
        neutral: Math.round((5 / 65) * 100),
      },

      priority_counts: {
        high: Math.round(65 * 0.2),
        medium: Math.round(65 * 0.35),
        low: 65 - Math.round(65 * 0.2) - Math.round(65 * 0.35),
      },
      priority_percentages: {
        high: Math.round((Math.round(65 * 0.2) / 65) * 100),
        medium: Math.round((Math.round(65 * 0.35) / 65) * 100),
        low: Math.round(
          ((65 -
            Math.round(65 * 0.2) -
            Math.round(65 * 0.35)) /
            65) *
            100
        ),
      },
      
      label_distribution: {
        checkin_process: {
          counts: { positive: 18, negative: 19, neutral: 3 },
          percentage: {
            positive: Math.round((18 / 40) * 100),
            negative: Math.round((19 / 40) * 100),
            neutral: Math.round((3 / 40) * 100),
          },
        },
        boarding_process: {
          counts: { positive: 12, negative: 11, neutral: 2 },
          percentage: {
            positive: Math.round((12 / 25) * 100),
            negative: Math.round((11 / 25) * 100),
            neutral: Math.round((2 / 25) * 100),
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 5, negative: 3, neutral: 1 },
        day_2: { positive: 5, negative: 4, neutral: 0 },
        day_3: { positive: 4, negative: 5, neutral: 0 },
        day_4: { positive: 5, negative: 5, neutral: 0 },
        day_5: { positive: 4, negative: 6, neutral: 0 },
        day_6: { positive: 4, negative: 6, neutral: 0 },
        day_7: { positive: 3, negative: 1, neutral: 4 },
      },

      high_priority_samples: {
        checkin_process: [
          "Check-in queue was extremely long.",
          "Priority and regular lines were not clearly separated.",
          "Few staff were available to assist at the kiosks.",
        ],
        boarding_process: [
          "Boarding groups were not respected at the gate.",
          "Announcements about boarding order were unclear.",
          "Passengers were held in the jet bridge with no updates.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["TGS"],
      total: 420,

      sentiment_counts: {
        positive: 272,
        negative: 123,
        neutral: 25,
      },
      sentiment_percentages: {
        positive: Math.round((272 / 420) * 100),
        negative: Math.round((123 / 420) * 100),
        neutral: Math.round((25 / 420) * 100),
      },

      priority_counts: {
        high: 75,
        medium: 190,
        low: 155,
      },
      priority_percentages: {
        high: Math.round((75 / 420) * 100),
        medium: Math.round((190 / 420) * 100),
        low: Math.round((155 / 420) * 100),
      },


      label_distribution: {
        checkin_process: {
          counts: { positive: 170, negative: 80, neutral: 10 },
          percentage: {
            positive: Math.round((170 / 260) * 100),
            negative: Math.round((80 / 260) * 100),
            neutral: Math.round((10 / 260) * 100),
          },
        },
        boarding_process: {
          counts: { positive: 102, negative: 43, neutral: 15 },
          percentage: {
            positive: Math.round((102 / 160) * 100),
            negative: Math.round((43 / 160) * 100),
            neutral: Math.round((15 / 160) * 100),
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 60, negative: 15, neutral: 3 },
        week_2: { positive: 55, negative: 28, neutral: 4 },
        week_3: { positive: 45, negative: 20, neutral: 4 },
        week_4: { positive: 112, negative: 60, neutral: 14 },
      },

      high_priority_samples: {
        checkin_process: [
          "Check-in queue extended outside the rope barriers.",
          "Self check-in kiosks were not working and no staff assisted.",
          "Priority and regular queues were not clearly separated.",
        ],
        boarding_process: [
          "Boarding order was not followed, causing congestion at the gate.",
          "Announcements about boarding groups were unclear.",
          "Passengers were kept waiting in the jet bridge with no updates.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["TGS"],
      total: 3700,

      sentiment_counts: {
        positive: 2920,
        negative: 630,
        neutral: 150,
      },
      sentiment_percentages: {
        positive: Math.round((2920 / 3700) * 100),
        negative: Math.round((630 / 3700) * 100),
        neutral: Math.round((150 / 3700) * 100),
      },

      priority_counts: {
        high: Math.round(3700 * 0.23),
        medium: Math.round(3700 * 0.27),
        low:
          3700 -
          Math.round(3700 * 0.23) -
          Math.round(3700 * 0.27),
      },
      priority_percentages: {
        high: Math.round((Math.round(3700 * 0.23) / 3700) * 100),
        medium: Math.round((Math.round(3700 * 0.27) / 3700) * 100),
        low: Math.round(
          ((3700 -
            Math.round(3700 * 0.23) -
            Math.round(3700 * 0.27)) /
            3700) *
            100
        ),
      },

      label_distribution: {
        checkin_process: {
          counts: { positive: 1860, negative: 360, neutral: 70 },
          percentage: {
            positive: Math.round((1860 / 2290) * 100),
            negative: Math.round((360 / 2290) * 100),
            neutral: Math.round((70 / 2290) * 100),
          },
        },
        boarding_process: {
          counts: { positive: 1060, negative: 270, neutral: 80 },
          percentage: {
            positive: Math.round((1060 / 1410) * 100),
            negative: Math.round((270 / 1410) * 100),
            neutral: Math.round((80 / 1410) * 100),
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 260, negative: 90, neutral: 10 },
        month_2: { positive: 270, negative: 95, neutral: 10 },
        month_3: { positive: 280, negative: 100, neutral: 10 },
        month_4: { positive: 290, negative: 110, neutral: 10 },
        month_5: { positive: 300, negative: 115, neutral: 10 },
        month_6: { positive: 310, negative: 120, neutral: 10 },
        month_7: { positive: 315, negative: 125, neutral: 10 },
        month_8: { positive: 310, negative: 125, neutral: 10 },
        month_9: { positive: 300, negative: 120, neutral: 10 },
        month_10: { positive: 290, negative: 115, neutral: 10 },
        month_11: { positive: 280, negative: 110, neutral: 10 },
        month_12: { positive: 315, negative: 115, neutral: 10 },
      },

      high_priority_samples: {
        checkin_process: [
          "Seasonal peaks created very long queues at check-in.",
          "Staffing levels felt insufficient at peak times.",
          "Priority services did not always feel prioritized.",
        ],
        boarding_process: [
          "Boarding delays were frequent during busy months.",
          "Crowding at the gate made boarding stressful.",
          "Communication about last-minute gate changes was sometimes unclear.",
        ],
      },
    },
  },

  /* ===================== RVBCM ===================== */
  RVBCM: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["RVBCM"],
      total: 60,

      sentiment_counts: {
        positive: 41,
        negative: 15,
        neutral: 4,
      },
      sentiment_percentages: {
        positive: Math.round((41 / 60) * 100),
        negative: Math.round((15 / 60) * 100),
        neutral: Math.round((4 / 60) * 100),
      },

      priority_counts: {
        high: Math.round(60 * 0.2),
        medium: Math.round(60 * 0.35),
        low: 60 - Math.round(60 * 0.2) - Math.round(60 * 0.35),
      },
      priority_percentages: {
        high: Math.round((Math.round(60 * 0.2) / 60) * 100),
        medium: Math.round((Math.round(60 * 0.35) / 60) * 100),
        low: Math.round(
          ((60 -
            Math.round(60 * 0.2) -
            Math.round(60 * 0.35)) /
            60) *
            100
        ),
      },


      label_distribution: {
        booking_and_ticketing: {
          counts: { positive: 41, negative: 15, neutral: 4 },
          percentage: {
            positive: Math.round((41 / 60) * 100),
            negative: Math.round((15 / 60) * 100),
            neutral: Math.round((4 / 60) * 100),
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 6, negative: 2, neutral: 0 },
        day_2: { positive: 5, negative: 2, neutral: 1 },
        day_3: { positive: 6, negative: 2, neutral: 0 },
        day_4: { positive: 7, negative: 3, neutral: 0 },
        day_5: { positive: 7, negative: 3, neutral: 0 },
        day_6: { positive: 5, negative: 2, neutral: 1 },
        day_7: { positive: 5, negative: 1, neutral: 2 },
      },

      high_priority_samples: {
        booking_and_ticketing: [
          "Ticket change rules were not clearly shown during purchase.",
          "Encountered errors while trying to modify the ticket online.",
          "Refund timeline information was incomplete on the website.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["RVBCM"],
      total: 90,

      sentiment_counts: {
        positive: 58,
        negative: 27,
        neutral: 5,
      },
      sentiment_percentages: {
        positive: Math.round((58 / 90) * 100),
        negative: Math.round((27 / 90) * 100),
        neutral: Math.round((5 / 90) * 100),
      },

      priority_counts: {
        high: 10,
        medium: 40,
        low: 40,
      },
      priority_percentages: {
        high: Math.round((10 / 90) * 100),
        medium: Math.round((40 / 90) * 100),
        low: Math.round((40 / 90) * 100),
      },


      label_distribution: {
        booking_and_ticketing: {
          counts: { positive: 58, negative: 27, neutral: 5 },
          percentage: {
            positive: Math.round((58 / 90) * 100),
            negative: Math.round((27 / 90) * 100),
            neutral: Math.round((5 / 90) * 100),
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 15, negative: 8, neutral: 0 },
        week_2: { positive: 14, negative: 7, neutral: 2 },
        week_3: { positive: 16, negative: 8, neutral: 1 },
        week_4: { positive: 13, negative: 4, neutral: 2 },
      },

      high_priority_samples: {
        booking_and_ticketing: [
          "Ticket change fees were not clear at the time of purchase.",
          "Had difficulty modifying my ticket through the website.",
          "Refund timeline and rules were not explained transparently.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["RVBCM"],
      total: 2200,

      sentiment_counts: {
        positive: 1740,
        negative: 360,
        neutral: 100,
      },
      sentiment_percentages: {
        positive: Math.round((1740 / 2200) * 100),
        negative: Math.round((360 / 2200) * 100),
        neutral: Math.round((100 / 2200) * 100),
      },

      priority_counts: {
        high: Math.round(2200 * 0.23),
        medium: Math.round(2200 * 0.27),
        low:
          2200 -
          Math.round(2200 * 0.23) -
          Math.round(2200 * 0.27),
      },
      priority_percentages: {
        high: Math.round((Math.round(2200 * 0.23) / 2200) * 100),
        medium: Math.round((Math.round(2200 * 0.27) / 2200) * 100),
        low: Math.round(
          ((2200 -
            Math.round(2200 * 0.23) -
            Math.round(2200 * 0.27)) /
            2200) *
            100
        ),
      },


      label_distribution: {
        booking_and_ticketing: {
          counts: { positive: 1740, negative: 360, neutral: 100 },
          percentage: {
            positive: Math.round((1740 / 2200) * 100),
            negative: Math.round((360 / 2200) * 100),
            neutral: Math.round((100 / 2200) * 100),
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 160, negative: 40, neutral: 5 },
        month_2: { positive: 170, negative: 40, neutral: 5 },
        month_3: { positive: 170, negative: 45, neutral: 5 },
        month_4: { positive: 180, negative: 45, neutral: 5 },
        month_5: { positive: 180, negative: 40, neutral: 5 },
        month_6: { positive: 190, negative: 45, neutral: 5 },
        month_7: { positive: 190, negative: 45, neutral: 5 },
        month_8: { positive: 185, negative: 40, neutral: 5 },
        month_9: { positive: 180, negative: 40, neutral: 5 },
        month_10: { positive: 180, negative: 35, neutral: 5 },
        month_11: { positive: 170, negative: 35, neutral: 5 },
        month_12: { positive: 165, negative: 40, neutral: 5 },
      },

      high_priority_samples: {
        booking_and_ticketing: [
          "Booking change rules varied between channels over the year.",
          "Refund processing time was longer during peak travel seasons.",
          "Promo tickets had stricter change conditions than expected.",
        ],
      },
    },
  },
  /* ===================== CMYM ===================== */
  CMYM: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["CMYM"],
      total: 7,

      sentiment_counts: {
        positive: 5,
        negative: 1,
        neutral: 1,
      },
      sentiment_percentages: {
        positive: Math.round((5 / 7) * 100),
        negative: Math.round((1 / 7) * 100),
        neutral: Math.round((1 / 7) * 100),
      },

      priority_counts: {
        high: 1,
        medium: 2,
        low: 4,
      },
      priority_percentages: {
        high: Math.round((1 / 7) * 100),
        medium: Math.round((2 / 7) * 100),
        low: Math.round((4 / 7) * 100),
      },


      label_distribution: {
        customer_support: {
          counts: { positive: 5, negative: 1, neutral: 1 },
          percentage: {
            positive: Math.round((5 / 7) * 100),
            negative: Math.round((1 / 7) * 100),
            neutral: Math.round((1 / 7) * 100),
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 1, negative: 0, neutral: 0 },
        day_2: { positive: 1, negative: 0, neutral: 0 },
        day_3: { positive: 1, negative: 0, neutral: 0 },
        day_4: { positive: 1, negative: 0, neutral: 0 },
        day_5: { positive: 1, negative: 1, neutral: 0 },
        day_6: { positive: 0, negative: 0, neutral: 1 },
        day_7: { positive: 0, negative: 0, neutral: 0 },
      },

      high_priority_samples: {
        customer_support: [
          "Call wait time was long considering the issue urgency.",
          "Needed multiple calls to fully resolve the problem.",
          "Information provided by different agents was inconsistent.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["CMYM"],
      total: 70,

      sentiment_counts: {
        positive: 44,
        negative: 21,
        neutral: 5,
      },
      sentiment_percentages: {
        positive: Math.round((44 / 70) * 100),
        negative: Math.round((21 / 70) * 100),
        neutral: Math.round((5 / 70) * 100),
      },

      priority_counts: {
        high: 8,
        medium: 28,
        low: 34,
      },
      priority_percentages: {
        high: Math.round((8 / 70) * 100),
        medium: Math.round((28 / 70) * 100),
        low: Math.round((34 / 70) * 100),
      },


      label_distribution: {
        customer_support: {
          counts: { positive: 44, negative: 21, neutral: 5 },
          percentage: {
            positive: Math.round((44 / 70) * 100),
            negative: Math.round((21 / 70) * 100),
            neutral: Math.round((5 / 70) * 100),
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 10, negative: 4, neutral: 1 },
        week_2: { positive: 12, negative: 5, neutral: 0 },
        week_3: { positive: 12, negative: 7, neutral: 1 },
        week_4: { positive: 10, negative: 5, neutral: 3 },
      },

      high_priority_samples: {
        customer_support: [
          "Call wait time was over 20 minutes during disruption.",
          "Issue required multiple calls and was not solved in one contact.",
          "Different agents gave conflicting information about my case.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["CMYM"],
      total: 1900,

      sentiment_counts: {
        positive: 1540,
        negative: 280,
        neutral: 80,
      },
      sentiment_percentages: {
        positive: Math.round((1540 / 1900) * 100),
        negative: Math.round((280 / 1900) * 100),
        neutral: Math.round((80 / 1900) * 100),
      },

      priority_counts: {
        high: Math.round(1900 * 0.23),
        medium: Math.round(1900 * 0.27),
        low:
          1900 -
          Math.round(1900 * 0.23) -
          Math.round(1900 * 0.27),
      },
      priority_percentages: {
        high: Math.round((Math.round(1900 * 0.23) / 1900) * 100),
        medium: Math.round((Math.round(1900 * 0.27) / 1900) * 100),
        low: Math.round(
          ((1900 -
            Math.round(1900 * 0.23) -
            Math.round(1900 * 0.27)) /
            1900) *
            100
        ),
      },


      label_distribution: {
        customer_support: {
          counts: { positive: 1540, negative: 280, neutral: 80 },
          percentage: {
            positive: Math.round((1540 / 1900) * 100),
            negative: Math.round((280 / 1900) * 100),
            neutral: Math.round((80 / 1900) * 100),
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 140, negative: 25, neutral: 5 },
        month_2: { positive: 145, negative: 25, neutral: 5 },
        month_3: { positive: 150, negative: 25, neutral: 5 },
        month_4: { positive: 155, negative: 30, neutral: 5 },
        month_5: { positive: 150, negative: 25, neutral: 5 },
        month_6: { positive: 160, negative: 30, neutral: 5 },
        month_7: { positive: 160, negative: 30, neutral: 5 },
        month_8: { positive: 155, negative: 25, neutral: 5 },
        month_9: { positive: 150, negative: 25, neutral: 5 },
        month_10: { positive: 145, negative: 25, neutral: 5 },
        month_11: { positive: 145, negative: 25, neutral: 5 },
        month_12: { positive: 145, negative: 30, neutral: 5 },
      },

      high_priority_samples: {
        customer_support: [
          "High call volumes in holiday seasons led to long waits.",
          "Some agents gave inconsistent information about disruptions.",
          "Callbacks were sometimes delayed or missed.",
        ],
      },
    },
  },
  /* ===================== GYB ===================== */
  GYB: {
    weekly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["GYB"],
      total: 23,

      sentiment_counts: {
        positive: 17,
        negative: 4,
        neutral: 2,
      },
      sentiment_percentages: {
        positive: Math.round((17 / 23) * 100),
        negative: Math.round((4 / 23) * 100),
        neutral: Math.round((2 / 23) * 100),
      },

      priority_counts: {
        high: 5,
        medium: 8,
        low: 10,
      },
      priority_percentages: {
        high: Math.round((5 / 23) * 100),
        medium: Math.round((8 / 23) * 100),
        low: Math.round((10 / 23) * 100),
      },


      label_distribution: {
        pricing_and_loyalty: {
          counts: { positive: 17, negative: 4, neutral: 2 },
          percentage: {
            positive: Math.round((17 / 23) * 100),
            negative: Math.round((4 / 23) * 100),
            neutral: Math.round((2 / 23) * 100),
          },
        },
      },

      period_label: "Last 7 days",

      historical_data: {
        day_1: { positive: 3, negative: 1, neutral: 0 },
        day_2: { positive: 2, negative: 1, neutral: 0 },
        day_3: { positive: 3, negative: 1, neutral: 0 },
        day_4: { positive: 3, negative: 1, neutral: 0 },
        day_5: { positive: 3, negative: 1, neutral: 0 },
        day_6: { positive: 2, negative: 0, neutral: 1 },
        day_7: { positive: 1, negative: 0, neutral: 1 },
      },

      high_priority_samples: {
        pricing_and_loyalty: [
          "Ticket prices changed significantly within a short time window.",
          "Award seats were not available on popular flights.",
          "Miles accrual rules for the booked fare were not clear.",
        ],
      },
    },

    monthly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["GYB"],
      total: 60,

      sentiment_counts: {
        positive: 38,
        negative: 18,
        neutral: 4,
      },
      sentiment_percentages: {
        positive: Math.round((38 / 60) * 100),
        negative: Math.round((18 / 60) * 100),
        neutral: Math.round((4 / 60) * 100),
      },

      priority_counts: {
        high: 7,
        medium: 23,
        low: 30,
      },
      priority_percentages: {
        high: Math.round((7 / 60) * 100),
        medium: Math.round((23 / 60) * 100),
        low: Math.round((30 / 60) * 100),
      },


      label_distribution: {
        pricing_and_loyalty: {
          counts: { positive: 38, negative: 18, neutral: 4 },
          percentage: {
            positive: Math.round((38 / 60) * 100),
            negative: Math.round((18 / 60) * 100),
            neutral: Math.round((4 / 60) * 100),
          },
        },
      },

      period_label: "Last 30 days",

      historical_data: {
        week_1: { positive: 9, negative: 4, neutral: 1 },
        week_2: { positive: 10, negative: 5, neutral: 1 },
        week_3: { positive: 11, negative: 5, neutral: 1 },
        week_4: { positive: 8, negative: 4, neutral: 1 },
      },

      high_priority_samples: {
        pricing_and_loyalty: [
          "Ticket prices fluctuated significantly within a few hours.",
          "Award seat availability was limited on popular routes.",
          "Loyalty miles rules for this fare were not clearly explained.",
        ],
      },
    },

    yearly: {
      department_name: DEPARTMENT_CODE_TO_LABEL["GYB"],
      total: 850,

      sentiment_counts: {
        positive: 570,
        negative: 240,
        neutral: 40,
      },
      sentiment_percentages: {
        positive: Math.round((570 / 850) * 100),
        negative: Math.round((240 / 850) * 100),
        neutral: Math.round((40 / 850) * 100),
      },

      priority_counts: {
        high: Math.round(850 * 0.23),
        medium: Math.round(850 * 0.27),
        low:
          850 -
          Math.round(850 * 0.23) -
          Math.round(850 * 0.27),
      },
      priority_percentages: {
        high: Math.round((Math.round(850 * 0.23) / 850) * 100),
        medium: Math.round((Math.round(850 * 0.27) / 850) * 100),
        low: Math.round(
          ((850 -
            Math.round(850 * 0.23) -
            Math.round(850 * 0.27)) /
            850) *
            100
        ),
      },

      label_distribution: {
        pricing_and_loyalty: {
          counts: { positive: 570, negative: 240, neutral: 40 },
          percentage: {
            positive: Math.round((570 / 850) * 100),
            negative: Math.round((240 / 850) * 100),
            neutral: Math.round((40 / 850) * 100),
          },
        },
      },

      period_label: "Last 12 months",

      historical_data: {
        month_1: { positive: 60, negative: 20, neutral: 3 },
        month_2: { positive: 65, negative: 20, neutral: 3 },
        month_3: { positive: 70, negative: 20, neutral: 3 },
        month_4: { positive: 75, negative: 25, neutral: 3 },
        month_5: { positive: 70, negative: 20, neutral: 3 },
        month_6: { positive: 75, negative: 25, neutral: 3 },
        month_7: { positive: 80, negative: 25, neutral: 3 },
        month_8: { positive: 75, negative: 25, neutral: 3 },
        month_9: { positive: 70, negative: 20, neutral: 3 },
        month_10: { positive: 70, negative: 20, neutral: 3 },
        month_11: { positive: 69, negative: 20, neutral: 3 },
        month_12: { positive: 81, negative: 20, neutral: 4 },
      },

      high_priority_samples: {
        pricing_and_loyalty: [
          "Dynamic pricing during peak periods frustrated frequent flyers.",
          "Award seat availability was limited on popular routes.",
          "Loyalty benefits were perceived as weaker after fare changes.",
        ],
      },
    },
  },
};
