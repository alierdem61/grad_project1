// Define Tuples
tuple Arc {
    int i;   // Start node of the arc
    int j;   // End node of the arc
};

// Define Sets
{int} I = ...;                   // Set of cells
{int} S_o = ...;                 // Set of source cells
{int} S_e = ...;                 // Set of sink cells
{int} R = ...;                   // Set of road segment cells
{int} R_prime = ...;             // Subset of road segment cells with downstream nodes
{int} T = ...;                   // Set of evacuation time periods
{int} Tp = ...;                  // Set of disaster time periods (T')
{Arc} A = ...;                   // Set of arcs as tuples (i, j)
{int} P = ...;                   // Set of resources
{int} Vp = ...;                  // Set of nodes eligible for resource allocation

// Parameters
int D[i in S_o] = ...;              // Evacuation demand for source cell i
float Q[i in R] = ...;                // Capacity of road segment cell i
float c[i in I][t in Tp] = ...;       // Risk coefficient for cell i at time t
float N[i in R] = ...;                // Holding capacity for cell i
float s_factor[i in R] = ...;            // Speed ratio for cell i
int tau[p in P][n1 in Vp][n2 in Vp] = ...;  // Travel time for resource p between nodes n1 and n2
int tau_max[p in P][n in Vp] = ...;         // Precomputed maximum travel time for resource p at node n

float delta[i in R] = ...; // Assume capacity increase from resource allocation is delta for each i in I_n

// Mapping: Road segment cell to downstream node
int downstreamNode[i in R_prime] = ...;  // Maps cell i in R_prime to its downstream node

// Decision Variables
dvar int+ x[I][T];            // Number of vehicles in cell i at time t
dvar int+ y[A][T];            // Vehicle flow on arc (i,j) at time t

// Expression 17 & 18
dvar boolean z[Vp][P][T];       // Resource allocation at node n for resource p at time t
dvar boolean e[S_o];            // Evacuation decision for source cell i

// Objective Function
minimize 
  sum(i in I, t in T) c[i][t] * x[i][t] +
  sum(i in S_o, t in Tp) D[i] * c[i][t] * (1 - e[i]);

// Constraints
subject to {
    // Flow Balance (Expression 2)
    forall (i in I, t in T: t > 1)
        x[i][t] == x[i][t-1] +
                  sum(a in A: a.j == i) y[a][t-1] -
                  sum(a in A: a.i == i) y[a][t-1];

    // Total Evacuation by Time T (Expression 3)
    sum(i in S_e) x[i][card(T)] == sum(i in S_o) D[i] * e[i];

    // Capacity Constraints (Expressions 4-9)
    forall (i in R, t in T: t < card(T))
      // Expression 4
        sum(a in A: a.j == i) y[a][t] <= s_factor[i] * (N[i] - x[i][t]);

    forall (i in I, t in T: t < card(T))
      // Expression 5
        sum(a in A: a.i == i) y[a][t] <= x[i][t];

	forall (i in R diff R_prime, t in T: t < card(T)) {
	    // Expression 6
	    sum(a in A: a.j == i) y[a][t] <= Q[i];
	    
	    // Expression 7
	    sum(a in A: a.i == i) y[a][t] <= Q[i];
	}

	forall (i in R_prime, t in T: t < card(T)) {
	    // Updated constraints for flow
	    sum(a in A: a.j == i) y[a][t] <= Q[i] + sum(p in P: downstreamNode[i] in Vp) z[downstreamNode[i]][p][t] * delta[i];
	    sum(a in A: a.i == i) y[a][t] <= Q[i] + sum(p in P: downstreamNode[i] in Vp) z[downstreamNode[i]][p][t] * delta[i];
	}

    // Resource Allocation (Expressions 10-12)
    // Expression 10
    forall (n in Vp, t in T)
        sum(p in P) z[n][p][t] <= 1;

	// Expression 11
    forall (p in P, t in T)
        sum(n in Vp) z[n][p][t] <= 1;

	// Expression 12
    // Fixed t2 filter using precomputed tau_max
    forall (n in Vp, p in P, t1 in T, t2 in T: t2 - t1 <= tau_max[p][n])
        z[n][p][t1] + sum(n2 in Vp: t1 + tau[p][n][n2] >= t2) z[n2][p][t2] <= 1;

    // Initial Conditions (Expressions 13-14)
    // Expression 13
    forall (i in S_o)
        x[i][1] == D[i] * e[i];

	// Expression 14
    forall (i in I diff S_o)
        x[i][1] == 0;

    // Non-Negativity (Expressions 15-16)
    forall (i in I, t in T)
        x[i][t] >= 0;

    forall (a in A, t in T: t < card(T))
        y[a][t] >= 0;

}

execute {
    // Write evacuation decisions to CSV format
    writeln("evac.csv:");
    for (i in S_o)
        writeln(i, ",", e[i]);
    
    // Write vehicle counts in cells over time to CSV format
    writeln("vehicles.csv:");
    for (i in I) {
        for (t in T) {
            write(x[i][t]);
            if (t < T.size) 
                write(",");
            else
                writeln();
        }
    }
}

