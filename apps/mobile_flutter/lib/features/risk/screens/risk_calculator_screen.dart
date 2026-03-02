import 'package:flutter/material.dart';
import '../../../../core/localization/app_localizations.dart';

class RiskCalculatorScreen extends StatefulWidget {
  const RiskCalculatorScreen({super.key});

  @override
  State<RiskCalculatorScreen> createState() => _RiskCalculatorScreenState();
}

class _RiskCalculatorScreenState extends State<RiskCalculatorScreen> {
  final _balanceController = TextEditingController(text: '100');
  final _riskPercentController = TextEditingController(text: '2');
  final _maxTradesController = TextEditingController(text: '5');
  final _maxLossesController = TextEditingController(text: '3');
  double? _suggestedStake;

  @override
  void dispose() {
    _balanceController.dispose();
    _riskPercentController.dispose();
    _maxTradesController.dispose();
    _maxLossesController.dispose();
    super.dispose();
  }

  void _calculate() {
    final balance = double.tryParse(_balanceController.text) ?? 0;
    final riskPercent = double.tryParse(_riskPercentController.text) ?? 0;
    final maxTrades = int.tryParse(_maxTradesController.text) ?? 1;

    if (balance > 0 && riskPercent > 0 && maxTrades > 0) {
      final riskAmount = balance * (riskPercent / 100);
      final stake = riskAmount / maxTrades;
      setState(() {
        _suggestedStake = stake;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.riskCalculator),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _balanceController,
              decoration: InputDecoration(
                labelText: localizations.balance,
                prefixText: '\$',
                border: const OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _riskPercentController,
              decoration: InputDecoration(
                labelText: localizations.riskPercent,
                suffixText: '%',
                border: const OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _maxTradesController,
              decoration: InputDecoration(
                labelText: localizations.maxTradesPerDay,
                border: const OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _maxLossesController,
              decoration: InputDecoration(
                labelText: localizations.maxConsecutiveLosses,
                border: const OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: _calculate,
              child: Text(localizations.calculate),
            ),
            if (_suggestedStake != null) ...[
              const SizedBox(height: 32),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text(
                        localizations.suggestedStake,
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '\$${_suggestedStake!.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.displaySmall,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

