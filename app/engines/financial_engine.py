from typing import List


class FinancialEngine:

    def calculate_vpl(self, cashflows: List[float], discount_rate: float) -> float:
        vpl = 0.0

        for t, cf in enumerate(cashflows):
            vpl += cf / ((1 + discount_rate) ** t)

        return round(vpl, 2)

    def calculate_vgv(self, prices: List[float]) -> float:
        return round(sum(prices), 2)

    def calculate_tir(self, cashflows: List[float], guess: float = 0.1) -> float:

        rate = guess

        for _ in range(1000):

            npv = 0.0
            d_npv = 0.0

            for t, cf in enumerate(cashflows):

                denom = (1 + rate) ** t
                npv += cf / denom

                if t > 0:
                    d_npv -= t * cf / ((1 + rate) ** (t + 1))

            if abs(npv) < 1e-6:
                return round(rate, 6)

            if abs(d_npv) < 1e-10:
                break

            rate -= npv / d_npv

        return round(rate, 6)

    def evaluate_project(self, cashflows: List[float], discount_rate: float):

        vpl = self.calculate_vpl(cashflows, discount_rate)

        return {
            "metric": "vpl",
            "vpl": vpl,
            "cashflow_count": len(cashflows),
            "discount_rate": discount_rate
        }
