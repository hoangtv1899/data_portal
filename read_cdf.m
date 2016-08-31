function contents = read_cdf(file)
    contents = containers.Map;
    ncid=netcdf.open(file,'nowrite');
    % CDF Data information
    [numdims, numvars, numglobalatts, unlimdimID] = netcdf.inq(ncid);
    for i = 0:numvars-1
        [varname, xtype, dimids, numatts] = netcdf.inqVar(ncid,i);
        flag = 0;
        for j = 0:numatts - 1
            attname1 = netcdf.inqAttName(ncid,i,j);
            attname2 = netcdf.getAtt(ncid,i,attname1);
            disp([attname1 ':  ' num2str(attname2)])
            if strmatch('add_offset',attname1)
                offset = attname2;
            end
            if strmatch('scale_factor',attname1)
                scale = attname2;
                flag = 1;
            end
        end
        if flag
            contents(varname) = double(double(netcdf.getVar(ncid,i))*scale +offset);
        else
            contents(varname) = double(netcdf.getVar(ncid,i));
        end
    end
    netcdf.close(ncid);
end