import plotly.plotly as py
import plotly.graph_objs as go
import plotly 

# ---------------- Time taken for varying number of gates ---------------

# Add data
num_of_gates = [7, 127, 255, 511, 1023, 4095, 8191]
bid_len_1_tsub = [0.000047, 0.000038, 0.000033, 0.000036, 0.000039, 0.000101, 0.000037]
bid_len_1_ttot = [0.740489, 1.656702, 2.609405, 4.624066, 11.12320, 34.15763, 55.33018]

bid_len_2_tsub = [0.000030, 0.000038, 0.000036, 0.000070, 0.000051, 0.000049, 0.000026]
bid_len_2_ttot = [0.672608, 1.691837, 2.691704, 6.515773, 10.83218, 36.49104, 64.03560]

bid_len_4_tsub = [0.000031, 0.000029, 0.000029, 0.000040, 0.000028, 0.000041, 0.000029]
bid_len_4_ttot = [0.671992, 1.528368, 2.312944, 4.164842, 8.040040, 27.90587, 54.46032]



trace0 = go.Scatter(
        x = num_of_gates,
        y = bid_len_1_tsub,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_1_tsub,
        textposition = 'top center',
        name = "1 bit",
        line = dict(
        color = ('rgb(205, 12, 24)'),
        width = 4)
        )

trace1 = go.Scatter(
        x = num_of_gates,
        y = bid_len_1_ttot,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_1_ttot,
        textposition = 'top center',
        name = "1 bit",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4,)
        )

trace2 = go.Scatter(
        x = num_of_gates,
        y = bid_len_2_tsub,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_1_tsub,
        textposition = 'top center',
        name = "2 bits",
        line = dict(
        color = ('rgb(205, 12, 24)'),
        width = 4,
        dash = 'dash')
        )

trace3 = go.Scatter(
        x = num_of_gates,
        y = bid_len_2_ttot,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_1_ttot,
        textposition = 'top center',
        name = "2 bits",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4,
        dash = 'dash')
        )

trace4 = go.Scatter(
        x = num_of_gates,
        y = bid_len_4_tsub,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_4_tsub,
        textposition = 'top center',
        name = "4 bits",
        line = dict(
        color = ('rgb(205, 12, 24)'),
        width = 4,
        dash = 'dot' )       
        )

trace5 = go.Scatter(
        x = num_of_gates,
        y = bid_len_4_ttot,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text = bid_len_4_ttot,
        textposition = 'top center',
        name = "4 bits",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4,
        dash = 'dot'  )      
        )

data = [trace0, trace2, trace4]

# Edit the layout
# Graph for tsub for different bit length inputs
layout = dict(title = 'Execution time for varying number of gates',
              xaxis = dict(title = 'Number of gates'),
              yaxis = dict(title = 'CPU time - tsub (sec)'),
              )

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig, filename='results/tsub',auto_open=True)

data = [trace1, trace3, trace5]

# Graph for ttot for different bit length inputs
layout = dict(title = 'Execution time for varying number of gates',
              xaxis = dict(title = 'Number of gates'),
              yaxis = dict(title = 'CPU time - ttot (sec)'),
              )

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig, filename='results/ttot',auto_open=True)


# ------------------- Time taken for varying gate type -----------------


# input bid length = 1 ttot
gate_and = [0.704504, 1.471810, 2.309473, 4.015701, 7.680686, 28.26563, 56.94533]
gate_xor = [0.669126, 1.453043, 2.302135, 4.093221, 8.536975, 28.04883, 60.63065]
gate_or = [0.727869, 1.508811, 2.601034, 3.873673, 7.199653, 27.68675, 56.15132]

trace6 = go.Scatter(
        x = num_of_gates,
        y = gate_and,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text =gate_and,
        textposition = 'top center',
        name = "AND",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4)
        )

trace7 = go.Scatter(
        x = num_of_gates,
        y = gate_or,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text =gate_or,
        textposition = 'top center',
        name = "OR",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4,
        dash = 'dash')
        )


trace8 = go.Scatter(
        x = num_of_gates,
        y = gate_xor,
        mode = 'lines+markers',
        #mode = 'lines+markers+text',
        text =gate_xor,
        textposition = 'top center',
        name = "XOR",
        line = dict(
        color = ('rgb(22, 96, 167)'),
        width = 4,
        dash = 'dot')
        )

data = [ trace6, trace7, trace8 ]
# Graph for ttot for different gate types 
layout = dict(title = 'Execution time for varying types of gates',
              xaxis = dict(title = 'Type of gate'),
              yaxis = dict(title = 'CPU time - ttot (sec)'),
              )

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig, filename='results/gate_type',auto_open=True)

# --------------- Time taken for varying length of primes ------------------

# prime lengths:
# OR gate, size of circuit - 128 gates
# profiling vpot time
prime_len = [12, 20, 50, 100, 500, 1000]
ttot = [1.395500, 1.451839, 1.395540, 1.417696, 1.401800, 1.539462]

