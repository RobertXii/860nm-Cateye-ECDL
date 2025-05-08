%% Goal 859.7 nm
%% Filter Transmission data
% data = readmatrix('Thorlab FBH860-10.xlsx');
% data = readmatrix('Semrock FF01-880-11-25.xlsx');
% data = readmatrix('Thorlab FBH870-10.xlsx');

% Define parameters
num_points = 200;
x = linspace(855, 885, num_points)';  % First column: range from 855 to 885 nm

% Gaussian parameters
center = 866;  % Center of Gaussian
FWHM = 1.2;    % Full Width at Half Maximum
sigma = FWHM / (2*sqrt(2*log(2)));  % Convert FWHM to standard deviation
gaussian = exp(-((x - center).^2) / (2 * sigma^2));
data = [x, gaussian];

wavelength_data = data(:,1);
transmission_data = data(:,2);
lambda = linspace(855, 875, 50000); % create plot wavelength range in nm

% Interpolate Transmission Data
T_filter = interp1(wavelength_data, transmission_data, lambda,'spline');

theta = 10.792;  % Initial angle of incidence
L_e = 0.03;  % Initial external cavity length (m)
Current = 25;  % system temperature in K

%% Initial Plot Setup
fig = figure('Name', 'Transmission Plot', 'Position', [100, 100, 800, 600]);
set(fig, 'UserData', struct('L_e', L_e, 'theta', theta, 'Current', Current));

axes('Position', [0.1, 0.2, 0.8, 0.7]);

% Slider for incident angle (theta)
theta_slider = uicontrol('Style', 'slider', ...
                         'Min', 0, 'Max', 20, 'Value', theta, ...
                         'Units', 'normalized', ...
                         'Position', [0.1 0 0.8 0.04]);
addlistener(theta_slider, 'ContinuousValueChange', ...
    @(src, ~) updateState(fig, 'theta', get(src, 'Value'), lambda, T_filter));

% Slider for Current
current_slider = uicontrol('Style', 'slider', ...
                           'Min', 0, 'Max', 100, 'Value', Current, ...
                           'Units', 'normalized', ...
                           'Position', [0.1 0.05 0.8 0.04]);
addlistener(current_slider, 'ContinuousValueChange', ...
    @(src, ~) updateState(fig, 'Current', get(src, 'Value'), lambda, T_filter));

% Slider for Length of external cavity (L_e)
L_e_slider = uicontrol('Style', 'slider', ...
                       'Min', 0.02998, 'Max', 0.03002, 'Value', L_e, ...
                       'Units', 'normalized', ...
                       'Position', [0.1 0.1 0.8 0.04]);
addlistener(L_e_slider, 'ContinuousValueChange', ...
    @(src, ~) updateState(fig, 'L_e', get(src, 'Value'), lambda, T_filter));

% Label for filter angle
uicontrol('Style', 'text', ...
          'String', 'Filter Angle', ...
          'Units', 'normalized', ...
          'Position', [0.01 0 0.08 0.04], ...
          'HorizontalAlignment', 'right', ...
          'FontSize', 12);

% Label for Current
uicontrol('Style', 'text', ...
          'String', 'Diode Current', ...
          'Units', 'normalized', ...
          'Position', [0.01 0.05 0.08 0.04], ...
          'HorizontalAlignment', 'right', ...
          'FontSize', 12);

% Label for Length of external cavity (L_e)
uicontrol('Style', 'text', ...
          'String', 'Cavity Length', ...
          'Units', 'normalized', ...
          'Position', [0.01 0.1 0.08 0.04], ...
          'HorizontalAlignment', 'right', ...
          'FontSize', 12);

% Initial plot call
updatePlot(L_e, theta, Current, lambda, T_filter);

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
    updatePlot(state.L_e, state.theta, state.Current, lambda, T_filter);
end

function updatePlot(L_e, theta, Current, lambda, T_filter)
    % Constant
    c = 299792458; % Speed of light in m/s
    
    % Diode laser constants
    FWHM_gain = 3.67; % Gain profile FWHM in nm 
    lambda0 = 859.7; % Central wavelength in nm

    % filter const
    theta = 14.865; % angle of incidence (degree)
    n_eff = 2.13; % Effective refractive index for p-polarization

    % Diode cavity constants, L_d in nm
    r1d = 0.75; % Reflectivity of diode's rear facet
    r2d = 0.25; % Reflectivity of diode's front facet
    alpha_d = 10^(-5); % thermal expansion coefficient of diode
    L_d = 0.25e-3 * (1 + alpha_d * Current); % diode cavity length (m) without feed-forward
    % L_d = 0.25e-3 * (1 + alpha_d * Current + (L_e - 0.03)/L_e); % coupled with L_e feed-forward
    n_d = 3.5; % diode refractive index

    % External cavity constants
    r1e = 0.3; % Reflectivity of external cavity's rear facet
    r2e = 0.5; % Reflectivity of external cavity's front facet
    n_e = 1; % external cavity refractive index

    % Coefficients of finesse
    F_d = 4 * r1d * r2d / (1 - r1d * r2d)^2; % for diode cavity
    F_e = 4 * r1e * r2e / (1 - r1e * r2e)^2; % for external cavity

    % Frequency range
    nu = c ./ (lambda * 1e-9);

    % Phase shifts
    delta_d = 2 * pi * n_d * L_d * nu / c; % for diode cavity
    delta_e = 2 * pi * n_e * L_e * nu / c; % for external cavity

    % Transmission functions
    T_d = 1 ./ (1 + F_d * sin(delta_d).^2); % for diode cavity
    T_e = 1 ./ (1 + F_e * sin(delta_e).^2); % for external cavity

    % Gain profile for laser diode (Gaussian)
    G_D = exp(-4 * log(2) * ((lambda - lambda0) / FWHM_gain).^2);

    % Filter transmission, algorithm for calculating shifted transmission
    % graph. This is an approximate calculation, where the transmission
    % curve remains its shape after shift
    [~, max_filter_value_id] = max(T_filter);
    max_filter_freq = max_filter_value_id * (lambda(end)-lambda(1))/50000 + lambda(1);
    max_filter_freq_shifted_id = round((max_filter_freq -(max_filter_freq ...
        * sqrt(1 - (sin(theta * pi / 180) / n_eff)^2))) * 50000 / (lambda(end)-lambda(1)));
    T_filter_shifted = [T_filter(1 + max_filter_freq_shifted_id:end), zeros(1, max_filter_freq_shifted_id)];
    % disp(max_filter_freq_shifted_id);

    % Total transmission
    T_total = G_D .* T_d .* T_e .* T_filter_shifted;
    [~, max_id] = max(T_total);
    max_wavelength = max_id * (lambda(end)-lambda(1))/50000 + lambda(1);
    max_freq = 299792458 / (max_wavelength * 1e3);

    freq = nu ./ (1e12); % translate into frequency domain

    %% Plots
    cla; % Clear previous plot
    hold on;
    plot(freq, T_total, 'LineWidth', 0.5, 'Color','k');
    xline(freq(max_id), '-', 'LineWidth', 1.5, 'Color', [1, 0, 0, 1]); % Vertical dashed red line represent the maximum

    plot(freq, G_D, '-', 'LineWidth', 1.5, 'Color', [0.2, 0.4, 0.8, 0.7]);
    plot(freq, T_filter_shifted, '-', 'LineWidth', 1.5, 'Color', [0.5, 0.5, 0.5, 0.7]);
    plot(freq, T_d, '-', 'LineWidth', 1.5, 'Color', [0.9, 0.6, 0.5, 0.5]);
    % plot(lambda, T_e, '-', 'LineWidth', 0.5, 'Color', [0.2, 0.2, 0.2, 0.3]);
    text(freq(max_id), 1.05, sprintf('%.5f nm\n%.5f THz', max_wavelength, max_freq), ...
        'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', ...
        'Color', 'r', 'FontSize', 15);
    set(gca, 'XDir', 'reverse'); % Flip the x-axis
    hold off;

    title(['Total Transmission vs \lambda ' newline ' (E.C. length = ' num2str(L_e*10^9, '%.2f') ...
       ' nm, angle = ' num2str(theta, '%.3f') ' degrees, Current = ' num2str(Current, '%.2f') ' )']);    
    xlabel('Frequency (THz)');
    ylabel('Transmission');
    legend('Total Transmission', 'maximum','Gain Profile', 'Filter Transmission', ...
           'Diode Cavity Transmission', 'External Cavity Transmission');
    grid on;
end

