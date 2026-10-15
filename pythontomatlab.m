function start_comsol_server()

    global COMSOL_MODEL; 

    fprintf('Loading COMSOL model once...\n');
    COMSOL_MODEL = mphload('pc.mph'); 
    COMSOL_MODEL.hist.disable;

    u = udpport("datagram", "LocalPort", 3031);
    configureCallback(u, "datagram", 1, @runComsolFromPath);
    cleanupObj = onCleanup(@() clear('u'));
    
    fprintf('MATLAB server is running and waiting for a file path from Python...\n');
    fprintf('Press Ctrl+C to stop.\n');
    
    while true
        pause(1);
    end
end


function runComsolFromPath(src, ~)
    global COMSOL_MODEL;
    
    try

        data_packet = read(src, 1, "string");
        txt_file_path = data_packet.Data;
        fprintf('\n--- New Task Received ---\n');
        fprintf('Received file path: %s\n', txt_file_path);

        if ~exist(txt_file_path, 'file')
            error('File received from Python does not exist: %s', txt_file_path);
        end

        txt_file_comsol = strrep(txt_file_path, '\', '\\');
        COMSOL_MODEL.component('comp1').geom('geom1').feature('pol1').set('filename', txt_file_comsol);
        fprintf('Updating geometry and mesh...\n');
        COMSOL_MODEL.component('comp1').geom('geom1').run;
        COMSOL_MODEL.component('comp1').mesh('mesh1').run;
        fprintf('Starting study...\n');
        COMSOL_MODEL.study('std1').run;
        fprintf('Extracting results...\n');
        COMSOL_MODEL.result.numerical('gev1').setResult;
        y_data = real(mphtable(COMSOL_MODEL,'tbl1').data);
        analysis_result = gap_analysis(y_data, 500, 0.1);
        optimization_target = analysis_result(end, 3); 
        fprintf('Calculation complete. Sending target value to Python: %.4f\n', optimization_target);
        
        write(src, optimization_target, "double", "localhost", 3030);
        
    catch ME
        fprintf('\n[ERROR] %s\n', ME.message);
        fprintf('Error in ==> %s at line %d\n', ME.stack(1).file, ME.stack(1).line);
        error_value = 0.0; 
        write(src, error_value, "double", "localhost", 3030);
    end
end