#https://beastfingersclimbing.com/training/strength-calculator
def _estimate_boulder_grade_from_mvc(weight, mvc):
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

print(_estimate_boulder_grade_from_mvc(78,48))
print(_estimate_boulder_grade_from_mvc(78,50))