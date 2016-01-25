using DataFrames
#using ClusterManagers
using ArgParse
using YAML
using Persist

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

function parse_csv_to_commands(csv_file, model_directory, outpath="./out/")
    data = readtable(csv_file)
    commands = []
    col_names = names(data)
    for (count, row) in enumerate(eachrow(data))
        command = row[1]
        for (i, name) in enumerate(col_names[2:end])
            command = join([command, row[i+1]], *(" ", replace(string(name), "_", "-"), " "))
            command = replace(command, "*OUTD*", outpath)
            command = replace(command, "*OUTF*", joinpath(outpath, join([basename(outpath), count], "_")))
            command = replace(command, "*MOD*", model_directory)
        end
        push!(commands, command)
    end
    return commands
end

function unpack_directory(model_directory, dir_name)
    output_dir = *(dir_name, "_out/") 
    output_path = joinpath(model_directory, "out", output_dir)
    mkpath(output_path)
    
    dir_path = joinpath(model_directory, "in", dir_name)
    dir_listing = readdir(dir_path)

    commands = []
    for item in dir_listing
        item_path = joinpath(dir_path, item)
        if !startswith(item, ".") && endswith(item, ".csv") && isfile(item_path)
            commands = vcat(parse_csv_to_commands(item_path, model_directory, output_path), commands)
        end
    end
    return commands
end
        
@everywhere function run_job(command, model_directory)
    cd(model_directory)
    return readall(`$command`)
    #run(`echo test`)
    #run(`$command`)
end


@everywhere function test_run_job()
    return readall(`echo test`)
end

function schedule_jobs(commands, output_dir, model_directory)
#function schedule_jobs()
    #job_num = length(commands)
    #node_num = 1
    job_num = 10

    #=
    addprocs(SlurmManager(job_num))
    output = []
    pids = []
    for i in workers()
        #host, pid = fetch(@spawnat i (run_job("ls", model_directory), getpid()))
        out, pid = fetch(@spawnat i (test_run_job(), getpid()))
        push!(output, out)
        push!(pids, pid)
    end
    println(output)

    for i in workers()
        rmprocs(i)
    end
    =#
    
    jobs = []
    for (count, command) in enumerate(commands)
        jobname = *("logopipe-", string(count)) 
        @persist jobname SlurmManager (cd(model_directory); run(`$command`))
        push!(jobs, readmgr(jobname))
    end
        
    while !all(map(isready, jobs))
        for status in map(status, jobs)
            println(status)
        end
        sleep(10)
        println("wating")
    end
end

function main()    
    args = parse_commandline()

    in_dir = joinpath(args["model_directory"], "in")
    out_dir = joinpath(args["model_directory"], "out")

    commands = []
    in_listing = readdir(in_dir)
    for dir in in_listing
        if !startswith(dir, ".") && isdir(joinpath(in_dir, dir))
            commands = vcat(unpack_directory(args["model_directory"], dir), commands)
        end
    end

    for command in commands
        println(command)
    end

    schedule_jobs(commands, out_dir, args["model_directory"])
end

main()
#schedule_jobs()

