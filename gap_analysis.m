function bandgap_regions = gap_analysis(data, target_max_freq, min_gap_threshold)
    freq_bands = data(:, 2:end)';

    n_points = size(freq_bands, 1);
    n_bands = size(freq_bands, 2);

    data_max_freq = max(freq_bands(:));

    if data_max_freq < target_max_freq
        analysis_max_freq = data_max_freq;
    else
        analysis_max_freq = target_max_freq;
    end

    band_max = zeros(n_bands, 1);
    band_min = zeros(n_bands, 1);

    for band = 1:n_bands
        band_freq = freq_bands(:, band);
        valid_freq = band_freq(band_freq >= 0 & band_freq <= analysis_max_freq);
        if ~isempty(valid_freq)
            band_max(band) = max(valid_freq);
            band_min(band) = min(valid_freq);
        else
            band_max(band) = NaN;
            band_min(band) = NaN;
        end
    end

    bandgap_regions = [];

    for band = 1:(n_bands - 1)
        if ~isnan(band_max(band)) && ~isnan(band_min(band + 1))
            if band_max(band) < band_min(band + 1)
                gap_start = band_max(band);
                gap_end = band_min(band + 1);
                gap_width = gap_end - gap_start;
                if gap_width > min_gap_threshold
                    bandgap_regions = [bandgap_regions; ...
                                       gap_start, gap_end, gap_width, band];
                end
            end
        end
    end

    if ~isempty(bandgap_regions)
        total_gap_width = sum(bandgap_regions(:, 3));
    else
        total_gap_width = 0;
    end

    summary_row = [NaN, NaN, total_gap_width, NaN];

    bandgap_regions = [bandgap_regions; summary_row];

end