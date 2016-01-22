using DataFrames
using ClusterManagers
using ArgParse
using YAML

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

function parse_csv_to_commands(csv_file, outpath="./out/")
    data = readtable(csv_file)
    commands = []
    col_names = names(data)
    for row in eachrow(data)
        command = row[1]
        for (i, name) in enumerate(col_names[2:end])
            command = join([command, row[i+1]], *(replace(string(name), "_", " -"), " "))
            command = replace(command, "OUT", outpath)
        end
        push!(commands, command)
    end
    return commands
end

function unpack_directory(model_directory, dir_name)
    output_dir = *(dir_name, "_out/") 
    output_path = join([model_directory, "out", output_dir], "/")
    mkpath(output_path)
    
    dir_path = join([model_directory, "in", dir_name], "/")
    dir_listing = readdir(dir_path)

    commands = []
    for item in dir_listing
        if !startswith(item, ".") && endswith(item, ".csv") && isfile(join([dir_path, item], "/"))
            csv_file_path = join([dir_path, item], "/")
            commands = vcat(parse_csv_to_commands(csv_file_path, output_path), commands)
        end
    end
    return commands
end
        
function run_job(command)
    run(`$command`)
end

function schedule_jobs(commands, output_dir)
    job_num = length(commands)
    node_num = 1

    #slurm_out = join([output_dir, "slurm_output"], "/")
    #mkdir(slurm_out)

    addprocs(SlurmManager(job_num), nodes=node_num)

    pmap(run_job, commands)
    #=
    @parallel for i in workers()
        run()
    end

    for i in workers()
        rmprocs(i)
    end
    =#
end

function main()    
    args = parse_commandline()

    in_dir = join([args["model_directory"], "in"], "/")
    out_dir = join([args["model_directory"], "out"], "/")

    commands = []
    in_listing = readdir(in_dir)
    for dir in in_listing
        if !startswith(dir, ".") && isdir(join([in_dir, dir], "/"))
            commands = vcat(unpack_directory(args["model_directory"], dir), commands)
        end
    end
    for command in commands
        println(command)
    end
    schedule_jobs(commands, out_dir)
end

main()

