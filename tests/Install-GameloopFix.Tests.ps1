#Requires -Modules Pester, PSScriptAnalyzer
#
# Smoke tests for the GameLoop Keymapping Fix installer.
#
# The installer is a Windows-targeted tool (registry, hosts file, Program Files),
# so it cannot run end-to-end on Linux/macOS. These tests validate the pieces
# that ARE portable: the script parses, it is clean under PSScriptAnalyzer, and
# its pure prompt/glyph helpers behave correctly. Console I/O (Read-Host /
# Write-Host) is mocked so the real functions from the script can be exercised.

BeforeAll {
    $script:ScriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'Install-GameloopFix.ps1'

    $tokens = $null
    $script:ParseErrors = $null
    $script:Ast = [System.Management.Automation.Language.Parser]::ParseFile(
        $script:ScriptPath, [ref]$tokens, [ref]$script:ParseErrors)

    # Pull individual function definitions out of the AST and load only those,
    # so importing the script does not trigger its top-level admin check / menu.
    $funcAsts = $script:Ast.FindAll(
        { param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)
    foreach ($name in 'U', 'Read-Choice', 'Read-YesNo', 'Read-Number') {
        $def = $funcAsts | Where-Object { $_.Name -eq $name } | Select-Object -First 1
        if ($def) { . ([ScriptBlock]::Create($def.Extent.Text)) }
    }
}

Describe 'Script integrity' {
    It 'parses without syntax errors' {
        $script:ParseErrors | Should -BeNullOrEmpty
    }

    It 'has no Error-severity PSScriptAnalyzer findings' {
        $errors = Invoke-ScriptAnalyzer -Path $script:ScriptPath -Severity Error
        $errors | Should -BeNullOrEmpty
    }
}

Describe 'Glyph helper (U)' {
    It 'builds a single unicode char from a code point' {
        U 0x221A | Should -BeExactly ([char]0x221A)   # check mark
        U 0x2192 | Should -BeExactly ([char]0x2192)   # right arrow
    }
    It 'joins multiple code points into a string' {
        U 0x41, 0x42, 0x43 | Should -BeExactly 'ABC'
    }
}

Describe 'Read-Number' {
    BeforeEach { Mock Write-Host {} }

    It 'returns a valid in-range parsed value' {
        Mock Read-Host { '6' }
        Read-Number -Prompt 'CPU' -Min 1 -Max 10 -Default 8 | Should -Be 6
    }
    It 'falls back to the default on non-numeric input' {
        Mock Read-Host { 'abc' }
        Read-Number -Prompt 'CPU' -Min 1 -Max 10 -Default 8 | Should -Be 8
    }
    It 'falls back to the default on out-of-range input' {
        Mock Read-Host { '99' }
        Read-Number -Prompt 'CPU' -Min 1 -Max 10 -Default 8 | Should -Be 8
    }
}

Describe 'Read-YesNo' {
    BeforeEach { Mock Write-Host {} }

    It 'returns $true for Y' {
        Mock Read-Host { 'y' }
        Read-YesNo -Prompt 'Enable?' -Default 'N' | Should -BeTrue
    }
    It 'returns $false for N' {
        Mock Read-Host { 'N' }
        Read-YesNo -Prompt 'Enable?' -Default 'Y' | Should -BeFalse
    }
    It 'uses the default for blank/invalid input' {
        Mock Read-Host { '' }
        Read-YesNo -Prompt 'Enable?' -Default 'Y' | Should -BeTrue
    }
}

Describe 'Read-Choice' {
    BeforeEach { Mock Write-Host {} }

    It 'returns the chosen key when valid' {
        Mock Read-Host { '2' }
        Read-Choice -Prompt 'Pick' -Default '1' -Options @{ '1' = 'A'; '2' = 'B' } | Should -Be '2'
    }
    It 'returns the default for an unknown key' {
        Mock Read-Host { '9' }
        Read-Choice -Prompt 'Pick' -Default '1' -Options @{ '1' = 'A'; '2' = 'B' } | Should -Be '1'
    }
}
