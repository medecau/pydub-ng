Pydub loves user contributions. 

We are happy to merge Pull Requests for features and bug fixes, of course. But, also spelling corrections, PEP 8 conformity, and platform-specific fixes.

Don't be shy!

### How to contribute:

1. Fork [pydub on github](https://github.com/medecau/pydub-ng)
2. Commit changes
3. Send a Pull Request

you did it! 

don't forget to append your name to the AUTHORS file ;)

There _are_ a few things that will make your Pull Request more likely to be merged:

1. Maintain backward compatibility
2. Avoid new dependencies
3. Include tests (and make sure they pass)
4. Write a short description of **what** is changed and **why**
5. Keep your Pull Request small, and focused on fixing one thing. 

  Smaller is easier to review, and easier to understand. 
  
  If you want to fix spelling and PEP 8 violations, send two pull requests :)
  
  
### Want to pitch in?
  
Take a look at our issue tracker for anything tagged [`bug`][bugs] or [`todo`][todos] - these are goals of the project and your improvements are _very_ likely to be merged!

That being said, there are many possible contributions we haven't thought of already. Those are welcome too!

Here are some general topics of interest for future development:

- Make it easier to get started with pydub
- More/better audio effects
- Support more audio formats
- Improve handling of large audio files
- Make things faster and use less memory.

### Releasing a New Version (Maintainers Only)

Publishing a new version of pydub-ng is automated via GitHub Actions once a release is created. Here's the process:

#### 1. Prepare the Release

**Update version number:**
```bash
# Edit pyproject.toml, update the version field (line 7)
version = "0.3.0"  # Update to your new version
```

**Update CHANGELOG.md:**
- Add a new section for the version with release notes
- Document what changed, fixed, or was added

**Commit the changes:**
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.3.0"
git push origin main
```

#### 2. Create GitHub Release

Wait for CI to pass on `main`, then create a release:

**Option A - Using GitHub CLI:**
```bash
gh release create v0.3.0 \
  --title "Brief descriptive title" \
  --notes "Release notes (can reference CHANGELOG.md)"
```

**Option B - Using GitHub Web UI:**
1. Go to https://github.com/medecau/pydub-ng/releases/new
2. Tag version: `v0.3.0` (match pyproject.toml version with `v` prefix)
3. Release title: Brief description
4. Description: Release notes or link to CHANGELOG
5. Click "Publish release"

#### 3. Automated Deployment

Once the release is created, GitHub Actions automatically:
1. Runs full test suite on Python 3.10-3.13
2. Builds the package using `uv build`
3. Publishes to PyPI using the `PYPI_API_TOKEN` secret

#### 4. Verify Publication

Check that the new version appears on PyPI:
```bash
# Check PyPI
open https://pypi.org/project/pydub-ng/

# Or test installation
pip install --upgrade pydub-ng
python -c "from pydub import AudioSegment; print(AudioSegment.__module__)"
```

#### Notes

- Version in `pyproject.toml` must be updated manually (not auto-generated)
- GitHub Release tag should match the version with `v` prefix (e.g., `v0.3.0`)
- PyPI publication happens automatically - no manual upload needed
- The `PYPI_API_TOKEN` repository secret must be configured for publishing to work

[bugs]: https://github.com/medecau/pydub-ng/issues?q=is%3Aissue+is%3Aopen+label%3Abug
[todos]: https://github.com/medecau/pydub-ng/issues?q=is%3Aissue+is%3Aopen+label%3Atodo
