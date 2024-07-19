import cudaq

# Set the backend target
cudaq.set_target('nvidia')

# We begin by defining the `Kernel` that we will construct our
# program with.
@cudaq.kernel()
def first_kernel():
    '''
    This is our first CUDA-Q kernel.
    '''
    # Next, we can allocate a single qubit to the kernel via `qubit()`.
    qubit = cudaq.qubit()

    # Now we can begin adding instructions to apply to this qubit!
    # Here we'll just add non-parameterized
    # single qubit gate that is supported by CUDA-Q.
    h(qubit)
    x(qubit)
    y(qubit)
    z(qubit)
    t(qubit)
    s(qubit)

    # Next, we add a measurement to the kernel so that we can sample
    # the measurement results on our simulator!
    mz(qubit)

print(cudaq.draw(first_kernel))

@cudaq.kernel
def second_kernel(N:int):
    qubits=cudaq.qvector(N)

    h(qubits[0])
    x.ctrl(qubits[0],qubits[1])
    x.ctrl(qubits[0],qubits[2])
    x(qubits)

    mz(qubits)

print(cudaq.draw(second_kernel,3))

@cudaq.kernel
def bar(N:int):
    qubits=cudaq.qvector(N)
    # front and back: return a direct refernce
    controls = qubits.front(N - 1)
    target = qubits.back()
    x.ctrl(controls, target)

print(cudaq.draw(bar,3))

@cudaq.kernel
def bell(N:int):
    qubits=cudaq.qvector(N)

    h(qubits[0])
    x.ctrl(qubits[0], qubits[1])

    mz(qubits)

print(cudaq.draw(bell,2))
# Sample the state generated by bell
# shots_count: the number of kernel executions. Default is 1000
counts = cudaq.sample(bell, 2, shots_count=10000)

# Print to standard out
print(counts)

# Fine-grained access to the bits and counts
for bits, count in counts.items():
    print('Observed: {}, {}'.format(bits, count))

@cudaq.kernel
def third_example(N:int, theta:list[float]):
    qubit=cudaq.qvector(N)

    h(qubit)

    for i in range(0,N//2):
        ry(theta[i],qubit[i])


    x.ctrl([qubit[0],qubit[1]],qubit[2]) #ccx
    x.ctrl([qubit[0],qubit[1],qubit[2]],qubit[3]) #cccx
    x.ctrl(qubit[0:3],qubit[3]) #cccx using Python slicing syntax

    mz(qubit)

params=[0.15,1.5]

print(cudaq.draw(third_example, 4, params))

result=cudaq.sample(third_example, 4, params, shots_count=5000)

print('Result: ', result)

print('Most probable bit string: ', result.most_probable())



@cudaq.kernel
def mid_circuit_m(theta:float):
    qubit=cudaq.qvector(2)
    ancilla=cudaq.qubit()

    ry(theta,ancilla)

    aux=mz(ancilla)
    if aux:
        x(qubit[0])
        x(ancilla)
    else:
        x(qubit[0])
        x(qubit[1])

    mz(ancilla)
    mz(qubit)

angle=0.5
result=cudaq.sample(mid_circuit_m, angle)
print(result)

# The example here shows a simple use case for the `cudaq.observe``
# function in computing expected values of provided spin hamiltonian operators.

from cudaq import spin

qubit_num=2

@cudaq.kernel
def init_state(qubits:cudaq.qview):
    n=qubits.size()
    for i in range(n):
        x(qubits[i])

@cudaq.kernel
def observe_example(theta: float):
    qvector = cudaq.qvector(qubit_num)

    init_state(qvector)
    ry(theta, qvector[1])
    x.ctrl(qvector[1], qvector[0])


spin_operator = 5.907 - 2.1433 * spin.x(0) * spin.x(1) - 2.1433 * spin.y(
0) * spin.y(1) + .21829 * spin.z(0) - 6.125 * spin.z(1)

# Pre-computed angle that minimizes the energy expectation of the `spin_operator`.
angle = 0.59

energy = cudaq.observe(observe_example, spin_operator, angle).expectation()
print(f"Energy is {energy}")

hamiltonian = 0.5*spin.z(0) + spin.x(1) + spin.y(0) + spin.y(0) * spin.y(1)+ spin.x(0)*spin.y(1)*spin.z(2)

# add some more terms
for i in range(2):
      hamiltonian += -2.0*spin.z(i)*spin.z(i+1)

print(hamiltonian)

print('Total number of terms in the spin hamiltonian: ',hamiltonian.get_term_count())

@cudaq.kernel
def param_circuit(theta: list[float]):
    # Allocate a qubit that is initialised to the |0> state.
    qubit = cudaq.qubit()
    # Define gates and the qubits they act upon.
    rx(theta[0], qubit)
    ry(theta[1], qubit)


# Our hamiltonian will be the Z expectation value of our qubit.
hamiltonian = spin.z(0)

# Initial gate parameters which initialize the qubit in the zero state
parameters = [0.0, 0.0]

print(cudaq.draw(param_circuit,parameters))

# Compute the expectation value using the initial parameters.
expectation_value = cudaq.observe(param_circuit, hamiltonian,parameters).expectation()

print('Expectation value of the Hamiltonian: ', expectation_value)

@cudaq.kernel
def kernel(N : int):
    q = cudaq.qvector(N)
    h(q[0])
    for i in range(N-1):
        x.ctrl(q[i], q[i+1])

# Look at the MLIR
print(kernel)

# Look at the QIR
print(cudaq.translate(kernel, format="qir"))
