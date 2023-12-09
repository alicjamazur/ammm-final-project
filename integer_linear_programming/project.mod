int                    n = ...;    // Number of orders.
int                    t = ...;    // Number of time slots
range                  N = 1..n;   // Range of orders.
range                  T = 1..t;   // Range  of time slots.
int            length[N] = ...;    // Time slots i-th order takes.
int       min_deliver[N] = ...;    // Min slot i-th order should be delivered.
int       max_deliver[N] = ...;    // Max slot i-th order should be delivered.
float          profit[N] = ...;    // Profit if I take i-th order.
float         surface[N] = ...;    // Surface of i-th order.
float   surface_capacity = ...;    // Surface capacity.

dvar boolean x_nt[n in N, t in T];
dvar boolean taken[n in N];

maximize sum(n in N) profit[n] * taken[n];

subject to {

	// If there is at least one time slot occupied, the order is taken
	 forall(n in N)
     	taken[n] == max(t in T) x_nt[n,t];

    // Oven surface constraint
    forall(t in T)
    	sum(n in N) (surface[n] * x_nt[n,t]) <= surface_capacity;

   	// Customer pickup time constraints
	forall(n in N)
	    min_deliver[n] * taken[n] <= max(t in T) (t * x_nt[n,t]);
	forall(n in N)
	    max_deliver[n] * taken[n] >= max(t in T) (t * x_nt[n,t]);

    // If the order is taken, the sum of occupied consecutive time slots is equal to the order preparation time
	forall(n in N) {
	    length[n] * taken[n] == max(start in T: start + length[n] - 1 <= t) sum(j in start..(start + length[n] - 1)) x_nt[n, j];
	}
}