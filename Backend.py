from flask import Flask, request, jsonify, render_template
from scipy.optimize import linprog

app = Flask(_name_)

def optimize_energy(min_req, cost_coeffs, max_limits):
    """
    Optimize energy consumption by minimizing cost.
    The problem:
        Minimize: cost1 * x1 + cost2 * x2
        Subject to: x1 + x2 >= min_req
                    0 <= x1 <= max1
                    0 <= x2 <= max2
    This constraint is converted as:
        -x1 - x2 <= -min_req
    """
    c = cost_coeffs
    A_ub = [[-1, -1]]
    b_ub = [-min_req]
    bounds = [(0, max_limits[0]), (0, max_limits[1])]

    # Using scipy's linprog with 'highs' method for improved performance
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return res

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    try:
        # Extract input parameters from the request
        min_req = float(data.get('min_req'))
        cost1 = float(data.get('cost1'))
        cost2 = float(data.get('cost2'))
        max1 = float(data.get('max1'))
        max2 = float(data.get('max2'))

        # Set up for two energy sources
        cost_coeffs = [cost1, cost2]
        max_limits = [max1, max2]

        # Run the optimization
        result = optimize_energy(min_req, cost_coeffs, max_limits)
        if result.success:
            response = {
                'success': True,
                'energy_allocations': {
                    'source1': result.x[0],
                    'source2': result.x[1]
                },
                'total_cost': result.fun
            }
        else:
            response = {
                'success': False,
                'message': 'Optimization failed: ' + result.message
            }
    except Exception as e:
        response = {
            'success': False,
            'message': str(e)
        }

    return jsonify(response)

if _name_ == '_main_':
    app.run(debug=True)