#include <stdio.h>
#include <mpi.h>

int main(int argc, char** argv) {
	FILE *output_file;

	output_file = fopen("active_hosts.txt", "a");
	
	int nprocs, myrank, name_len;
	char processor_name[MPI_MAX_PROCESSOR_NAME];

	MPI_Init(&argc, &argv);
	MPI_Get_processor_name(processor_name, &name_len);
	MPI_Comm_size(MPI_COMM_WORLD, &nprocs);
	MPI_Comm_rank(MPI_COMM_WORLD, &myrank);
	
	printf("Host %s ready to collaborate", processor_name);
	fputs(processor_name, output_file);

	MPI_Finalize();
	return 0;

}
