using DataFrames
using ClusterManagers
using ArgParse

function parse_commandline()
    settings = ArgParseSettings()
    settings.prog = "LogoPipe"
    settings.description = "LogoPipe is a custom application desinged to run NetLogo and Bsearch analyses with Slurm"
    @add_arg_table settings begin
        "model_directory"
            help = "The directory containing the model data"
            required = true
    end
    return parse_args(settings)
end

function parse_csv_to_command(csv_file)
    data = readtable(csv_file)
    commands = []
    col_names = names(data)
    for row in eachrow(data)
        command = "netlogo-headless.sh" #Working right now but could use retooling to make this work for any executable
        for (i, name) in enumerate(col_names)
            command = join([command, row[i]], *(replace(string(name), "_", " -"), " "))
        end
        push!(commands, command)
    end
    return commands
end
    
args = parse_commandline()
println(args)

in_dir = join([args["model_directory"], "in"], "/")
bsearch_dir = join([in_dir, "bsearch"], "/")
logo_dir = join([in_dir, "nlogo"], "/")

bfiles = readdir(bsearch_dir)
lfiles = readdir(logo_dir)

for file in bfiles
    full_path = join([bsearch_dir, file], "/")
    println(parse_bsearch_csv(full_path))
end
    
println(bfiles)

#Slurm scheduling
job_num = 2
node_num = 1

#=
addprocs(SlurmManager(job_num), nodes=node_num)

@parallel for i in workers()
    run(`hostname`)
end

for i in workers()
    rmprocs(i)
end
=#
