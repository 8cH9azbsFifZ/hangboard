"""
Class for estimating boulder grade from MVC according to
#https://beastfingersclimbing.com/training/strength-calculator


HOW TO USE
Our calculator helps to estimate your strength-to-weight ratio and one-arm hang, based on a liner regression of our data. Methods for used can be seen in our research , Optimizing Muscular Strength-to-Weight Ratios in Rock Climbing. Estimations are maximum volatile contraction (MVC) in peak forces for each grade on one hand.
Grades are represented in Hueco, Yosemite Decimal System (YDS), and French/Lead. Grades are adjusted for each rating and scale accordingly.

FINDING YOUR MAX
Using a 20mm edge or quad crimp on the 15° edge, there are two ways to find your max, by hanging or lifting. Using the Grippūl 2, you can increment your way up to max 5 Lbs at a time using a loading pin at 5 sec holds, and when you can't lift anymore, take that as your ! rep max. Using the Grippuūl XL, you can find your max hang by subtracting weight on the pulley system.
INCREASING FINGER STRENGTH
With testing done on healthy fingers 1-2 times a month. You can use our workout calculator below to increase finger strength. Remember rest, you should have no soreness, no pain, no tweaks when testing, climbing or during training.
"""

class EstimateBoulderGrade():
    def __init__(self, mvc = 66, weight = 99):
        self._mvc = mvc 
        self._weight = weight

    def Estimate(self):
        return self._estimate_boulder_grade_from_mvc(self._weight, self._mvc)

    def _estimate_boulder_grade_from_mvc(self, weight, mvc):
        multi = 0.74 / 2

        v = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        v[1] = weight * 0.38 * multi
        v[2] = weight * 0.76 * multi
        v[3] = weight * 0.8 * multi
        v[4] = weight * 0.97 * multi
        v[5] = weight * 1.6 * multi
        v[6] = weight * 1.64 * multi
        v[7] = weight * 1.69 * multi
        v[8] = weight * 2 * multi
        v[9] = weight * 2.4 * multi
        v[10] = weight * 2.65 * multi
        v[11] = weight * 2.76 * multi
        v[12] = weight * 2.82 * multi
        v[13] = weight * 3 * multi
        v[14] = weight * 3.22 * multi
        v[15] = weight * 3.45 * multi
        v[16] = weight * 3.64 * multi

        v1BW = (v[1] / weight * 100)
        v2BW = (v[2] / weight * 100)
        v3BW = (v[3] / weight * 100)
        v4BW = (v[4] / weight * 100)
        v5BW = (v[5] / weight * 100)
        v6BW = (v[6] / weight * 100)
        v7BW = (v[7] / weight * 100)
        v8BW = (v[8] / weight * 100)
        v9BW = (v[9] / weight * 100)
        v10BW = (v[10] / weight * 100)
        v11BW = (v[11] / weight * 100)
        v12BW = (v[12] / weight * 100)
        v13BW = (v[13] / weight * 100)
        v14BW = (v[14] / weight * 100)
        v15BW = (v[15] / weight * 100)
        v16BW = (v[16] / weight * 100)

        for i in range (0,16):
            if v[i] < mvc:
                continue
            else:
                return "V"+str(i-1)

    
if __name__ == "__main__":
    b = EstimateBoulderGrade(weight=78,mvc=48)
    print (b.Estimate())
