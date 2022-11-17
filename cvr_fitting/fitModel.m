% Uses fitnlm() to fit a non-linear model (an exponential decay curve) through noisy data.
fontSize = 20;

% Create the X coordinates from 0 to 20 every 0.5 units.
X = lawshetable.panel_size
Y = lawshetable.proportion

figure(1)
% Plot the noisy initial data.
plot(X, Y, 'b*', 'LineWidth', 2, 'MarkerSize', 15);
grid on;

% Convert X and Y into a table, which is the form fitnlm() likes the input data to be in.
tbl = table(X, Y);
% Define the model as Y = a + exp(-b*x)
% Note how this "x" of modelfun is related to big X and big Y.
% x((:, 1) is actually X and x(:, 2) is actually Y - the first and second columns of the table.
%modelfun = @(b,x) b(1) + b(2) * log(b(3).*x(:, 1)); 

modelfun = @(b,x) b(1) + b(2) * exp(-b(3)*x(:, 1));  

beta0 = [0, 10, 1]; % Guess values to start with.  Just make your best guess.

% Now the next line is where the actual model computation is done.
mdl = fitnlm(tbl, modelfun, beta0);
% Now the model creation is done and the coefficients have been determined.
% YAY!!!!

% Extract the coefficient values from the the model object.
% The actual coefficients are in the "Estimate" column of the "Coefficients" table that's part of the mode.
coefficients = mdl.Coefficients{:, 'Estimate'}
% Create smoothed/regressed data using the model:
X = 5:1:300
yFitted = coefficients(1) + coefficients(2) * exp(-coefficients(3)*X);

output = table;
output.panel_size = X';
output.n_critical = round(X'.*yFitted')
output.proportion = yFitted';

% Now we're done and we can plot the smooth model as a red line going through the noisy blue markers.
hold on;
plot(X, yFitted, 'r-', 'LineWidth', 2);
grid on;
title('Proportion Agreeing Essential Fitting', 'FontSize', fontSize);
xlabel('X', 'FontSize', fontSize);
ylabel('Y', 'FontSize', fontSize);
legendHandle = legend('Noisy Y', 'Fitted Y', 'Location', 'north');
legendHandle.FontSize = 25;

% Set up figure properties:
% Enlarge figure to full screen.
set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0 1 1]);
% Get rid of tool bar and pulldown menus that are along top of figure.
% set(gcf, 'Toolbar', 'none', 'Menu', 'none');
% Give a name to the title bar.
set(gcf, 'Name', 'Demo by ImageAnalyst', 'NumberTitle', 'Off') 

figure(2)
% Plot the noisy initial data.
plot(lawshetable.panel_size, lawshetable.n_critical, 'b*', 'LineWidth', 2, 'MarkerSize', 15);
title('N Critical Fitting', 'FontSize', fontSize);
grid on;
hold on;
plot(X, output.n_critical, 'r-', 'LineWidth', 2);


