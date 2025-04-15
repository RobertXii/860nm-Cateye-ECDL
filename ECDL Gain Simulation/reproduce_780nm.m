%% Filter Transmission data
data = [
    775, 4.10356799695128e-05;
    775.2, 5.69460783707786e-05;
    775.4, 8.01674651776898e-05;
    775.6, 0.00011463693331931;
    775.8, 0.00016675648605457;
    776, 0.000247176805744671;
    776.2, 0.000374066408108079;
    776.4, 0.000579283679285479;
    776.6, 0.000920423573722626;
    776.8, 0.0015051926243437;
    777, 0.00254271844403749;
    777.2, 0.00445628415485881;
    777.4, 0.0081424279099973;
    777.6, 0.0155929966938912;
    777.8, 0.0314369322638347;
    778, 0.0667192046710856;
    778.2, 0.1467507623289;
    778.4, 0.315926057372953;
    778.6, 0.587549057637158;
    778.8, 0.839323863320047;
    779, 0.958422461502881;
    779.2, 0.990344440716652;
    779.4, 0.996042113649083;
    779.6, 0.996793543924187;
    779.8, 0.99662004906238;
    780, 0.996394410160801;
    780.2, 0.996483831530391;
    780.4, 0.996524144750273;
    780.6, 0.995583837868906;
    780.8, 0.989645579705535;
    781, 0.958267464204696;
    781.2, 0.843214755801153;
    781.4, 0.598302512318159;
    781.6, 0.327635910420061;
    781.8, 0.154475053306327;
    782, 0.0709585611548745;
    782.2, 0.0336889212453174;
    782.4, 0.0168151002329152;
    782.6, 0.00883046374725106;
    782.8, 0.00485893037071326;
    783, 0.00278707198898805;
    783.2, 0.00165843585430921;
    783.4, 0.00101938923389622;
    783.6, 0.000644889042548756;
    783.8, 0.000418583671486604;
    784, 0.000278022838149285;
    784.2, 0.000188535972939269;
    784.4, 0.000130279316524914;
    784.6, 9.15777839395202e-05;
    784.8, 6.53881567170639e-05;
    785, 4.73633889165964e-05
];

wavelength_data = data(:,1);
transmission_data = data(:,2);
lambda = linspace(776, 784, 20000); % create plot wavelength range in nm

% Interpolate Transmission Data
T_filter = interp1(wavelength_data, transmission_data, lambda,'spline');

theta = 0;   % Initial angle of incidence
L_e = 0.03;   % Initial external cavity length

%% Initial Plot Setup
fig = figure('Name', 'Interactive Transmission Plot', 'Position', [100, 100, 800, 600]);
set(fig, 'UserData', struct('L_e', L_e, 'theta', theta));

axes('Position', [0.1, 0.2, 0.8, 0.7]);

% Create slider for Length of external cavity
uicontrol('Style', 'slider',...
          'Min', 0.0299998, 'Max', 0.0300003, 'Value', L_e,...
          'Units', 'normalized',...
          'Position', [0.1 0.07 0.8 0.05],...
          'Callback', @(src, ~) updateState(fig, 'L_e', get(src, 'Value'), lambda, T_filter));

% Create slider for incident angle
uicontrol('Style', 'slider',...
          'Min', 0, 'Max', 10, 'Value', theta,... 
          'Units', 'normalized',...
          'Position', [0.1 0 0.8 0.05],...
          'Callback', @(src, ~) updateState(fig, 'theta', get(src, 'Value'), lambda, T_filter));

% Initial plot call
updatePlot(L_e, theta, lambda, T_filter);

%% Local Function
% Function to update the shared state and redraw the plot
function updateState(fig, field, newValue, lambda, T_filter)
    % Get the current state
    state = get(fig, 'UserData');
    
    % Update the specified field (L_e or theta)
    state.(field) = newValue;
    
    % Save the updated state back to the figure's UserData
    set(fig, 'UserData', state);
    
    % Redraw the plot with the updated values
    updatePlot(state.L_e, state.theta, lambda, T_filter);
end

function updatePlot(L_e, theta, lambda, T_filter)
    %% Constant
    c = 299792458; % Speed of light in m/s
    
    % Diode laser constants
    FWHM_gain = 10; % Gain profile FWHM in nm 
    lambda0 = 783; % Central wavelength in nm

    % filter const
    % theta = 14.5; % angle of incidence (degree)
    n_eff = 2.13; % Effective refractive index for p-polarization

    % Diode cavity constants, L_d in nm
    r1d = 0.85; % Reflectivity of diode's rear facet
    r2d = 0.15; % Reflectivity of diode's front facet
    L_d = 0.25e-3; % diode cavity length (m)
    n_d = 3.5; % diode refractive index

    % External cavity constants
    r1e = 0.85; % Reflectivity of external cavity's rear facet
    r2e = 0.15; % Reflectivity of external cavity's front facet
    n_e = 1; % external cavity refractive index

    % Coefficients of finesse
    F_d = 4 * r1d * r2d / (1 - r1d * r2d)^2;% for diode cavity
    F_e = 4 * r1e * r2e / (1 - r1e * r2e)^2;% for external cavity

    % Frequency range
    nu = c ./ (lambda * 1e-9);

    % Phase shifts
    delta_d = 2 * pi * n_d * L_d * nu / c;% for diode cavity
    delta_e = 2 * pi * n_e * L_e * nu / c;% for external cavity

    % Transmission functions
    T_d = 1 ./ (1 + F_d * sin(delta_d).^2); % for diode cavity
    T_e = 1 ./ (1 + F_e * sin(delta_e).^2); % for external cavity

    % Gain profile for laser diode (Gaussian)
    G_D = exp(-4 * log(2) * ((lambda - lambda0) / FWHM_gain).^2);

    % Filter transmission, algorithm for calculating shifted transmission
    % graph. This is an approximate calculation, where the transmission
    % curve remains its shape after shift
    [~, max_filter_value_id] = max(T_filter);
    max_filter_freq = max_filter_value_id * (lambda(end)-lambda(1))/20000 + lambda(1);
    max_filter_freq_shifted_id = round((max_filter_freq -(max_filter_freq ...
        * sqrt(1 - (sin(theta * pi / 180) / n_eff)^2))) * 20000 / (lambda(end)-lambda(1)));
    T_filter_shifted = [T_filter(1 + max_filter_freq_shifted_id:end), zeros(1, max_filter_freq_shifted_id)];
    % disp(max_filter_freq_shifted_id);

    % Total transmission
    T_total = G_D .* T_d .* T_e .* T_filter_shifted;
    [~, max_id] = max(T_total);
    max_freq = max_id * (lambda(end)-lambda(1))/20000 + lambda(1);

    %% Plots
    cla; % Clear previous plot
    hold on;
    plot(lambda, T_total, 'LineWidth', 1.5);
    xline(lambda(max_id), '-', 'LineWidth', 0.8, 'Color', [1, 0, 0, 1]); % Vertical dashed red line represent the maximum
    text(lambda(max_id), 0.95, sprintf('%.3f nm', max_freq), ...
    'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', 'Color', 'r', 'FontSize', 10);

    plot(lambda, G_D, '-', 'LineWidth', 0.5, 'Color', [0, 0.44, 0.741, 0.5]);
    plot(lambda, T_filter_shifted, '-', 'LineWidth', 1, 'Color', [0.5, 0.5, 0.5, 0.7]);
    plot(lambda, T_d, '-', 'LineWidth', 0.5, 'Color', [0.8, 0.3, 0.7, 0.5]);
    plot(lambda, T_e, '-', 'LineWidth', 0.5, 'Color', [0.2, 0.2, 0.2, 0.5]);
    hold off;

    title(['Total Transmission vs \lambda (E.C. length = ' num2str(L_e*10^9, '%.1f') ...
       ' nm, angle = ' num2str(theta, '%.3f') ' degrees )']);    xlabel('Wavelength (nm)');
    ylabel('Transmission');
    legend('Total Transmission', 'maximum','Gain Profile', 'Filter Transmission', ...
           'Diode Cavity Transmission', 'External Cavity Transmission');
    grid on;
end

